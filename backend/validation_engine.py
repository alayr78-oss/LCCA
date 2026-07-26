import math
from lcca_engine import LCCAEngine

class ValidationEngine:
    """
    RAM-DSS Phase 6 Validation Engine
    Performs Mathematical, Model, and Sensitivity validations.
    """

    # -------------------------------------------------------------------------
    # 1. Mathematical Validation
    # -------------------------------------------------------------------------
    def validate_math_lcca(self, component, analysis_period, discount_rate, inflation_rate):
        """
        Validates Python LCCA engine NPV calculation against strict algebraic manual formulas
        to guarantee calculation accuracy.
        """
        engine = LCCAEngine(country_profile={'inflation_rate': inflation_rate, 'labour_cost_factor': 1, 'material_cost_factor': 1})
        result = engine.simulate_component_lifecycle(component, analysis_period, discount_rate)
        
        # Manual calculation (algebraic sum)
        manual_npv = 0
        real_rate = ((1 + discount_rate) / (1 + inflation_rate)) - 1
        
        for t, cost in enumerate(result['cash_flow_undiscounted']):
            if cost != 0:
                manual_npv += cost / ((1 + real_rate) ** t)
                
        # Compare
        difference_pct = abs((result['npv'] - manual_npv) / manual_npv * 100) if manual_npv != 0 else 0
        
        return {
            'ram_dss_npv': result['npv'],
            'manual_npv': manual_npv,
            'difference_percentage': round(difference_pct, 4),
            'accuracy_result': "Pass" if difference_pct < 0.1 else "Fail"
        }

    # -------------------------------------------------------------------------
    # 2. Model Validation (RMSE/MAE)
    # -------------------------------------------------------------------------
    def validate_deterioration_model(self, predicted_curve, observed_data_points):
        """
        Calculates Root Mean Square Error (RMSE) and Mean Absolute Error (MAE) 
        between predicted condition curve and actual historical inspections.
        """
        if not observed_data_points:
            return {'rmse': 0, 'mae': 0, 'message': 'No observed data'}

        squared_errors = []
        abs_errors = []
        
        for obs in observed_data_points:
            year = obs['year']
            observed_cond = obs['condition_rating']
            
            if year < len(predicted_curve):
                predicted_cond = predicted_curve[year]
                
                squared_errors.append((observed_cond - predicted_cond) ** 2)
                abs_errors.append(abs(observed_cond - predicted_cond))
                
        n = len(squared_errors)
        if n == 0:
             return {'rmse': 0, 'mae': 0}
             
        rmse = math.sqrt(sum(squared_errors) / n)
        mae = sum(abs_errors) / n
        
        return {
            'rmse': round(rmse, 2),
            'mae': round(mae, 2),
            'data_points_validated': n
        }

    # -------------------------------------------------------------------------
    # 3. Sensitivity Validation
    # -------------------------------------------------------------------------
    def run_sensitivity_analysis(self, base_scenario, ranges):
        """
        Generates data for Tornado charts by varying parameters across specific ranges.
        ranges = {
            'discount_rate': [0.05, 0.08, 0.11], # [Min, Base, Max]
            'material_cost_factor': [0.8, 1.0, 1.2],
            ...
        }
        """
        results = []
        base_engine = LCCAEngine(country_profile=base_scenario['country_profile'])
        base_result = base_engine.calculate_project_lcca(
            base_scenario['components'], 
            base_scenario['analysis_period'], 
            base_scenario['country_profile'].get('discount_rate', 0.08)
        )
        base_npv = base_result['total_npv']
        
        for param, values in ranges.items():
            if len(values) != 3: continue
            min_val, _, max_val = values
            
            # Test Min
            temp_scenario_min = dict(base_scenario)
            if param == 'discount_rate':
                temp_min_npv = LCCAEngine(country_profile=temp_scenario_min['country_profile']).calculate_project_lcca(
                    temp_scenario_min['components'], temp_scenario_min['analysis_period'], min_val
                )['total_npv']
            elif param == 'material_cost_factor':
                temp_profile = dict(temp_scenario_min['country_profile'])
                temp_profile['material_cost_factor'] = min_val
                temp_min_npv = LCCAEngine(country_profile=temp_profile).calculate_project_lcca(
                    temp_scenario_min['components'], temp_scenario_min['analysis_period'], temp_scenario_min['country_profile'].get('discount_rate', 0.08)
                )['total_npv']
            else:
                temp_min_npv = base_npv # Placeholder for other parameters
                
            # Test Max
            temp_scenario_max = dict(base_scenario)
            if param == 'discount_rate':
                temp_max_npv = LCCAEngine(country_profile=temp_scenario_max['country_profile']).calculate_project_lcca(
                    temp_scenario_max['components'], temp_scenario_max['analysis_period'], max_val
                )['total_npv']
            elif param == 'material_cost_factor':
                temp_profile = dict(temp_scenario_max['country_profile'])
                temp_profile['material_cost_factor'] = max_val
                temp_max_npv = LCCAEngine(country_profile=temp_profile).calculate_project_lcca(
                    temp_scenario_max['components'], temp_scenario_max['analysis_period'], temp_scenario_max['country_profile'].get('discount_rate', 0.08)
                )['total_npv']
            else:
                temp_max_npv = base_npv
                
            impact_swing = abs(temp_max_npv - temp_min_npv)
            
            results.append({
                'parameter': param,
                'base_value': base_npv,
                'min_value': temp_min_npv,
                'max_value': temp_max_npv,
                'impact_swing': impact_swing
            })
            
        # Sort by impact swing for Tornado Chart
        results.sort(key=lambda x: x['impact_swing'], reverse=True)
        return results
