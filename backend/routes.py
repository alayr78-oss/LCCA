from flask import Blueprint, jsonify, request
from models import db, Project, Asset, Component, Material, KnowledgeParameter, Reference, FailureMode, MaintenanceStrategy, CountryProfile, User, InspectionHistory, MaintenanceHistory, Scenario

api = Blueprint('api', __name__)

# --- Generic CRUD helper ---
def generic_get_all(model):
    records = model.query.all()
    # Simple dictionary serialization for basic fields
    return jsonify([{c.name: getattr(r, c.name) for c in model.__table__.columns} for r in records])

# --- Users ---
@api.route('/users', methods=['GET'])
def get_users(): return generic_get_all(User)

# --- Projects ---
@api.route('/projects', methods=['GET'])
def get_projects(): return generic_get_all(Project)

@api.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    p = Project(**{k: v for k, v in data.items() if hasattr(Project, k)})
    db.session.add(p)
    db.session.commit()
    return jsonify({"id": p.id}), 201

# --- Assets ---
@api.route('/assets', methods=['GET'])
def get_assets(): return generic_get_all(Asset)

@api.route('/assets', methods=['POST'])
def create_asset():
    data = request.json
    a = Asset(**{k: v for k, v in data.items() if hasattr(Asset, k)})
    db.session.add(a)
    db.session.commit()
    return jsonify({"id": a.id}), 201

# --- Components ---
@api.route('/components', methods=['GET'])
def get_components(): return generic_get_all(Component)

# --- Materials ---
@api.route('/materials', methods=['GET'])
def get_materials(): return generic_get_all(Material)

# --- Knowledge & References ---
@api.route('/references', methods=['GET'])
def get_references(): return generic_get_all(Reference)

@api.route('/knowledge', methods=['GET'])
def get_knowledge(): return generic_get_all(KnowledgeParameter)

# --- History ---
@api.route('/inspections', methods=['GET'])
def get_inspections(): return generic_get_all(InspectionHistory)

@api.route('/maintenance', methods=['GET'])
def get_maintenance(): return generic_get_all(MaintenanceHistory)

# --- Scenarios ---
@api.route('/scenarios', methods=['GET'])
def get_scenarios(): return generic_get_all(Scenario)

# --- Engines ---
from condition_engine import ConditionEngine

@api.route('/engine/condition', methods=['POST'])
def calculate_condition():
    data = request.json
    if not data or 'components' not in data:
        return jsonify({"error": "Missing 'components' array in request"}), 400
        
    deterioration_rate = data.get('deterioration_rate')
    if deterioration_rate is None or float(deterioration_rate) <= 0:
        return jsonify({"error": "Valid deterioration_rate > 0 is required"}), 400

    engine = ConditionEngine()
    
    # 1. Calculate ICI
    components = data['components']
    ici_result = engine.calculate_ici(components)
    
    # 2. Predict RSL
    rsl_result = engine.calculate_rsl(
        current_condition=ici_result['ici'],
        deterioration_rate=float(deterioration_rate),
        model_type=data.get('model_type', 'Linear'), # String fallback is fine here as it's an enum
        critical_threshold=data.get('critical_threshold', 40) # Engineering default
    )
    
    return jsonify({
        "ici_result": ici_result,
        "rsl_result": rsl_result,
        "transparency": {
            "formula_ici": "ICI = Σ(CCI × Component Importance Weight)",
            "formula_rsl": "Linear: (Current - Threshold) / Rate | Exponential: -ln(Threshold / Current) / Rate",
            "model_selected": data.get('model_type', 'Linear')
        }
    })

# --- LCCA Engine ---
from lcca_engine import LCCAEngine

@api.route('/lcca/calculate', methods=['POST'])
def lcca_calculate():
    data = request.json
    if not data or 'components' not in data or 'country_profile' not in data:
        return jsonify({"error": "Missing components or country_profile in request"}), 400

    analysis_period = data.get('analysis_period')
    discount_rate = data.get('discount_rate')
    
    if analysis_period is None or int(analysis_period) <= 0:
        return jsonify({"error": "Valid analysis_period > 0 is required"}), 400
    if discount_rate is None or float(discount_rate) <= 0:
        return jsonify({"error": "Valid discount_rate > 0 is required"}), 400

    cp = data['country_profile']
    if 'labour_cost_factor' not in cp or 'material_cost_factor' not in cp or 'inflation_rate' not in cp:
         return jsonify({"error": "Incomplete country_profile. Requires labour/material factors and inflation"}), 400

    engine = LCCAEngine(country_profile=cp)
    
    track_length_km = data.get('track_length_km', 1) # UI preference default is ok here
    
    result = engine.calculate_project_lcca(data['components'], int(analysis_period), float(discount_rate), track_length_km)
    
    return jsonify(result)

@api.route('/lcca/scenario_compare', methods=['POST'])
def lcca_scenario_compare():
    data = request.json
    scenarios = data.get('scenarios', [])
    
    results = []
    for s in scenarios:
        engine = LCCAEngine(country_profile=s.get('country_profile'))
        res = engine.calculate_project_lcca(
            s.get('components', []), 
            s.get('analysis_period', 50), 
            s.get('discount_rate', 0.08),
            s.get('track_length_km', 1)
        )
        # Store scenario name with result
        res['scenario_name'] = s.get('name', 'Scenario')
        results.append(res)
        
    return jsonify({"comparison": results})
# --- Phase 5: Decision Engine ---
from decision_engine import DecisionEngine

@api.route('/risk/calculate', methods=['POST'])
def risk_calculate():
    data = request.json
    engine = DecisionEngine()
    
    asset_condition = data.get('asset_condition', {'ici': 50, 'rsl_years': 10})
    consequence = data.get('consequence_factors', {'safety_impact': 8, 'operational_disruption': 7, 'traffic_importance': 9})
    
    result = engine.calculate_risk(asset_condition, consequence)
    return jsonify(result)

@api.route('/mcdm/rank', methods=['POST'])
def mcdm_rank():
    data = request.json
    engine = DecisionEngine(criteria_weights=data.get('weights'))
    
    alternatives = data.get('alternatives', [])
    ranking = engine.rank_alternatives(alternatives)
    
    return jsonify({"ranking": ranking})

@api.route('/recommendation/generate', methods=['POST'])
def recommendation_generate():
    data = request.json
    engine = DecisionEngine(criteria_weights=data.get('weights'))
    
    alternatives = data.get('alternatives', [])
    ranking = engine.rank_alternatives(alternatives)
    
    recommendation = engine.generate_recommendation(ranking)
    
    return jsonify({
        "ranking": ranking,
        "recommendation": recommendation,
        "transparency": {
            "mcdm_method": "Simple Additive Weighting (SAW)",
            "weights_used": engine.weights,
            "rule_basis": "Highest aggregated MCDM Score with inverted cost/risk/carbon metrics."
        }
    })

# --- Phase 6: Validation, Case Studies, and Export ---
from validation_engine import ValidationEngine
from export_engine import ExportEngine
from flask import send_file
import io

@api.route('/validation/run', methods=['POST'])
def validation_run():
    data = request.json
    if not data or 'component' not in data or 'observed_data' not in data:
         return jsonify({"error": "Missing component or observed_data for validation"}), 400
         
    engine = ValidationEngine()
    
    # Run math validation
    math_val = engine.validate_math_lcca(
        data['component'],
        data.get('analysis_period', 50),
        data.get('discount_rate', 0.08),
        data.get('inflation_rate', 0.02)
    )
    
    # Run sensitivity
    sens_val = engine.run_sensitivity_analysis(
        data.get('base_scenario', {
            'country_profile': {'discount_rate': 0.08, 'inflation_rate': 0.02, 'material_cost_factor': 1.0, 'labour_cost_factor': 1.0},
            'components': [data['component']],
            'analysis_period': 50
        }),
        data.get('ranges', {'discount_rate': [0.05, 0.08, 0.11]})
    )
    
    # Run model RMSE
    model_val = engine.validate_deterioration_model(
        data.get('predicted_curve', [100, 95, 90, 85, 80]),
        data['observed_data']
    )
    
    return jsonify({
        'mathematical_validation': math_val,
        'sensitivity_validation': sens_val,
        'model_validation': model_val
    })

@api.route('/export/report', methods=['POST'])
def export_report():
    data = request.json
    export_type = data.get('format', 'csv')
    
    if export_type == 'csv':
        csv_data = ExportEngine.generate_csv(data.get('report_data', {}))
        return send_file(io.BytesIO(csv_data.encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='ram_dss_report.csv')
    elif export_type == 'excel':
        excel_data = ExportEngine.generate_excel(data.get('report_data', {}))
        if isinstance(excel_data, str): # Error message
            return jsonify({"error": excel_data}), 400
        return send_file(io.BytesIO(excel_data), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='ram_dss_report.xlsx')
    elif export_type == 'pdf':
        pdf_data = ExportEngine.generate_pdf(data.get('report_data', {}))
        if isinstance(pdf_data, bytes) and pdf_data.startswith(b"FPDF2"): # Error
             return jsonify({"error": pdf_data.decode()}), 400
        return send_file(io.BytesIO(pdf_data), mimetype='application/pdf', as_attachment=True, download_name='ram_dss_report.pdf')
    
    return jsonify({"error": "Unknown format"}), 400
