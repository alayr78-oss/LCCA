import math

class ConditionEngine:
    """
    RAM-DSS Phase 3 Condition Assessment Engine
    Calculates Component Condition Index (CCI), Infrastructure Condition Index (ICI),
    models deterioration, and predicts Remaining Service Life (RSL).
    """

    def __init__(self, knowledge_base=None):
        # In a real app, this would be fetched from the DB KnowledgeParameter table
        self.kb = knowledge_base or {}

    def calculate_cci(self, parameter_ratings):
        """
        Calculate Component Condition Index (CCI)
        CCI = Σ(Parameter Rating × Parameter Weight)
        parameter_ratings: list of dicts [{'rating': 85, 'weight': 0.4}, ...]
        """
        cci = 0
        total_weight = 0
        for p in parameter_ratings:
            cci += p['rating'] * p['weight']
            total_weight += p['weight']
        
        # Normalize in case weights don't sum perfectly to 1
        return cci / total_weight if total_weight > 0 else 0

    def calculate_ici(self, component_conditions):
        """
        Calculate Infrastructure Condition Index (ICI)
        ICI = Σ(CCI × Component Importance Weight)
        component_conditions: list of dicts [{'cci': 75, 'weight': 0.35}, ...]
        """
        ici = 0
        total_weight = 0
        contributions = {}

        for comp in component_conditions:
            contribution = comp['cci'] * comp['weight']
            ici += contribution
            total_weight += comp['weight']
            contributions[comp['name']] = contribution
        
        normalized_ici = ici / total_weight if total_weight > 0 else 0

        # Calculate percentage contribution to the final score
        percentage_contributions = {}
        if normalized_ici > 0:
             percentage_contributions = {name: (val / ici) * 100 for name, val in contributions.items()}

        return {
            'ici': normalized_ici,
            'contributions': percentage_contributions,
            'classification': self.classify_condition(normalized_ici)
        }

    def classify_condition(self, score):
        # These thresholds could be dynamically loaded from the KB
        if score >= 80:
            return "Good"
        elif score >= 50:
            return "Moderate"
        else:
            return "Poor"

    def predict_deterioration(self, initial_condition, deterioration_rate, time_t, model_type="Linear"):
        """
        Predict future condition using selected model
        """
        if model_type == "Linear":
            return max(0, initial_condition - (deterioration_rate * time_t))
        elif model_type == "Exponential":
            # Condition(t) = Initial * exp(-rate * t)
            return initial_condition * math.exp(-deterioration_rate * time_t)
        else:
            raise ValueError("Unknown deterioration model")

    def calculate_rsl(self, current_condition, deterioration_rate, model_type, critical_threshold=40):
        """
        Calculate Remaining Service Life (RSL) based on selected deterioration model
        """
        if current_condition <= critical_threshold:
            return {
                'rsl_years': 0,
                'reason': f"Condition index ({current_condition:.1f}) is already at or below the critical threshold ({critical_threshold})."
            }

        rsl = 0
        if model_type == "Linear":
            # C(t) = C0 - r*t => t = (C0 - C(t)) / r
            rsl = (current_condition - critical_threshold) / deterioration_rate if deterioration_rate > 0 else 999
        elif model_type == "Exponential":
            # C(t) = C0 * exp(-r*t) => t = -ln(C(t)/C0) / r
            rsl = -math.log(critical_threshold / current_condition) / deterioration_rate if deterioration_rate > 0 else 999

        return {
            'rsl_years': round(rsl, 1),
            'reason': f"Condition index reaches critical threshold of {critical_threshold} after {round(rsl, 1)} years under current {model_type} deterioration rate."
        }
