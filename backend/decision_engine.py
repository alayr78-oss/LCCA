class DecisionEngine:
    """
    RAM-DSS Phase 5 Advanced Decision Support Engine
    Integrates Condition, LCCA, Risk Assessment, and MCDM to generate explainable recommendations.
    """

    def __init__(self, criteria_weights=None):
        # Fallback to default weights if none provided by the Knowledge Base
        self.weights = criteria_weights or {
            'lifecycle_cost': 0.30,
            'risk_score': 0.25,
            'reliability': 0.20,
            'carbon_footprint': 0.15,
            'maintenance_frequency': 0.10
        }

    # -------------------------------------------------------------------------
    # 1. Risk Assessment
    # -------------------------------------------------------------------------
    def calculate_risk(self, asset_condition, consequence_factors):
        """
        Risk = Probability of Failure (PoF) × Consequence of Failure (CoF)
        """
        # 1. Calculate Probability of Failure (0-10)
        # Lower condition index = higher probability of failure
        pof = 10 - (asset_condition['ici'] / 10) 
        if asset_condition.get('rsl_years', 50) < 3:
            pof = min(10, pof + 2) # Penalize if remaining service life is critically low

        # 2. Calculate Consequence of Failure (0-10)
        # Average of safety, operational disruption, traffic importance
        cof = (
            consequence_factors.get('safety_impact', 5) + 
            consequence_factors.get('operational_disruption', 5) + 
            consequence_factors.get('traffic_importance', 5)
        ) / 3.0

        # Risk Score (0-100)
        risk_score = pof * cof * (100 / 100) # Scaling max 10x10=100
        
        classification = "Low Risk"
        if risk_score >= 75: classification = "Critical Risk"
        elif risk_score >= 50: classification = "High Risk"
        elif risk_score >= 25: classification = "Medium Risk"

        return {
            'risk_score': round(risk_score, 1),
            'probability_of_failure': round(pof, 1),
            'consequence_of_failure': round(cof, 1),
            'classification': classification
        }

    # -------------------------------------------------------------------------
    # 2. Multi-Criteria Decision Making (MCDM)
    # -------------------------------------------------------------------------
    def rank_alternatives(self, alternatives):
        """
        Rank alternatives using a Simple Additive Weighting (SAW) method.
        Higher score is better. Costs and Risk are inverted.
        """
        # Normalize values to 0-100 scale (Assuming max possible values for inversion)
        MAX_COST = max(a['lifecycle_cost'] for a in alternatives) if alternatives else 1
        MAX_RISK = 100
        MAX_CARBON = max(a['carbon_footprint'] for a in alternatives) if alternatives else 1
        
        results = []
        for alt in alternatives:
            # Invert negative criteria (Cost, Risk, Carbon)
            norm_cost = 100 * (1 - (alt['lifecycle_cost'] / MAX_COST)) if MAX_COST > 0 else 0
            norm_risk = 100 * (1 - (alt['risk_score'] / MAX_RISK))
            norm_carbon = 100 * (1 - (alt['carbon_footprint'] / MAX_CARBON)) if MAX_CARBON > 0 else 0
            
            # Positive criteria
            norm_reliability = alt.get('reliability_score', 50)

            overall_score = (
                norm_cost * self.weights['lifecycle_cost'] +
                norm_risk * self.weights['risk_score'] +
                norm_reliability * self.weights['reliability'] +
                norm_carbon * self.weights['carbon_footprint']
            )

            results.append({
                'id': alt.get('id', 0),
                'name': alt['name'],
                'overall_score': round(overall_score, 1),
                'normalized_metrics': {
                    'cost': round(norm_cost, 1),
                    'risk': round(norm_risk, 1),
                    'carbon': round(norm_carbon, 1),
                    'reliability': round(norm_reliability, 1)
                }
            })

        # Sort descending by overall score
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        return results

    # -------------------------------------------------------------------------
    # 3. Explainable Recommendation
    # -------------------------------------------------------------------------
    def generate_recommendation(self, ranked_alternatives, baseline_alt=None):
        """
        Rule-based, explainable recommendation.
        """
        if not ranked_alternatives:
            return None
            
        best = ranked_alternatives[0]
        reasons = []
        
        # Build explanations
        if baseline_alt:
            cost_diff = baseline_alt['normalized_metrics']['cost'] - best['normalized_metrics']['cost']
            if cost_diff < 0:
                reasons.append(f"✓ Lowest lifecycle cost over analysis period")
            
            if best['normalized_metrics']['risk'] > baseline_alt['normalized_metrics']['risk']:
                reasons.append(f"✓ Reduced Risk Profile")
                
            if best['normalized_metrics']['carbon'] > baseline_alt['normalized_metrics']['carbon']:
                reasons.append(f"✓ Improved Environmental Sustainability (Carbon footprint reduced)")
        else:
            reasons = [
                "✓ Highest aggregated MCDM Score among alternatives.",
                f"✓ Strong performance in Cost Efficiency.",
                f"✓ Acceptable Risk profile."
            ]

        # Calculate a pseudo-confidence level based on score gap to second place
        confidence = 75
        if len(ranked_alternatives) > 1:
            gap = best['overall_score'] - ranked_alternatives[1]['overall_score']
            confidence = min(99, 75 + (gap * 2))

        return {
            'recommended_alternative': best['name'],
            'overall_score': best['overall_score'],
            'confidence_level': round(confidence, 1),
            'reasons': reasons
        }
