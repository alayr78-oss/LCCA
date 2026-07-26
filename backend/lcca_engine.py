import math

class LCCAEngine:
    """
    RAM-DSS Phase 4 Lifecycle Cost Analysis Engine
    Integrates condition assessment and remaining service life to dynamically simulate lifecycle costs,
    maintenance events, and carbon footprints.
    """

    def __init__(self, country_profile=None):
        # Country profile contains modifiers like inflation, labour_factor, material_factor
        self.country = country_profile or {
            'labour_cost_factor': 1.0,
            'material_cost_factor': 1.0,
            'inflation_rate': 0.02
        }

    def discount_factor(self, year, rate):
        """ Calculate Present Value (PV) discount factor """
        return 1 / ((1 + rate) ** year)

    def calculate_pv(self, future_cost, year, discount_rate, inflation_rate):
        """ Calculate Present Value considering inflation """
        real_rate = (1 + discount_rate) / (1 + inflation_rate) - 1
        return future_cost * self.discount_factor(year, real_rate)

    def calculate_eac(self, npv, discount_rate, analysis_period):
        """ Calculate Equivalent Annual Cost """
        if discount_rate == 0:
            return npv / analysis_period
        return npv * (discount_rate * ((1 + discount_rate) ** analysis_period)) / (((1 + discount_rate) ** analysis_period) - 1)

    def simulate_component_lifecycle(self, component, analysis_period, discount_rate):
        """
        Simulate the lifecycle of a single component based on its deterioration and costs.
        component = {
            'name': 'Rails',
            'initial_cost': 100000,
            'routine_maintenance_annual': 2000,
            'rehabilitation_cost': 50000,
            'replacement_cost': 110000,
            'salvage_value': 10000,
            'carbon_initial': 5000, # kg CO2
            'carbon_replacement': 5000,
            'rsl_years': 15, # Derived from Phase 3 Condition Engine
            'strategy': 'Condition-Based' # Preventive, Corrective, Condition-Based
        }
        """
        cash_flow = [0] * (analysis_period + 1)
        carbon_flow = [0] * (analysis_period + 1)
        
        # Year 0: Initial Construction
        adjusted_initial = component.get('initial_cost', 0) * self.country['material_cost_factor']
        cash_flow[0] += adjusted_initial
        carbon_flow[0] += component.get('carbon_initial', 0)
        
        interventions = 0
        rsl = component.get('rsl_years', analysis_period)
        
        # Simulate over analysis period
        for year in range(1, analysis_period + 1):
            # Routine Maintenance
            annual_maint = component.get('routine_maintenance_annual', 0) * self.country['labour_cost_factor']
            cash_flow[year] += annual_maint
            
            # Rehabilitation / Replacement Trigger (Condition-based)
            if year > 0 and year % rsl == 0:
                interventions += 1
                adjusted_replace = component.get('replacement_cost', 0) * self.country['material_cost_factor']
                cash_flow[year] += adjusted_replace
                carbon_flow[year] += component.get('carbon_replacement', 0)
                
        # Year N: Salvage Value
        adjusted_salvage = component.get('salvage_value', 0) * self.country['material_cost_factor']
        cash_flow[analysis_period] -= adjusted_salvage
        
        # Calculate PV for each year to get NPV
        npv = 0
        inflation = self.country.get('inflation_rate', 0.02)
        discounted_cash_flow = []
        for year, cost in enumerate(cash_flow):
            pv = self.calculate_pv(cost, year, discount_rate, inflation)
            npv += pv
            discounted_cash_flow.append(pv)
            
        eac = self.calculate_eac(npv, discount_rate, analysis_period)
        total_carbon = sum(carbon_flow)
        
        return {
            'name': component['name'],
            'npv': npv,
            'eac': eac,
            'total_carbon': total_carbon,
            'interventions': interventions,
            'cash_flow_undiscounted': cash_flow,
            'cash_flow_discounted': discounted_cash_flow
        }

    def calculate_project_lcca(self, components, analysis_period=50, discount_rate=0.08, track_length_km=1):
        """
        Aggregate component lifecycles into a total project LCCA.
        """
        results = []
        total_npv = 0
        total_eac = 0
        total_carbon = 0
        
        # Aggregate yearly cash flow
        project_cash_flow = [0] * (analysis_period + 1)
        
        for comp in components:
            res = self.simulate_component_lifecycle(comp, analysis_period, discount_rate)
            results.append(res)
            total_npv += res['npv']
            total_eac += res['eac']
            total_carbon += res['total_carbon']
            
            for i, val in enumerate(res['cash_flow_discounted']):
                project_cash_flow[i] += val

        # Calculate percentage contributions
        contributions = {}
        if total_npv > 0:
            contributions = {r['name']: (r['npv'] / total_npv) * 100 for r in results}

        # Calculate Cost Per Kilometre
        cpk = total_npv / track_length_km if track_length_km > 0 else total_npv

        return {
            'total_npv': total_npv,
            'total_eac': total_eac,
            'total_carbon': total_carbon,
            'cost_per_km': cpk,
            'component_breakdown': results,
            'contributions': contributions,
            'project_cash_flow': project_cash_flow,
            'transparency': {
                'discount_rate': discount_rate,
                'inflation_rate': self.country.get('inflation_rate'),
                'analysis_period': analysis_period,
                'formula_npv': 'Σ (CashFlow_t / (1 + real_rate)^t)',
                'formula_eac': 'NPV * (r(1+r)^n) / ((1+r)^n - 1)'
            }
        }
