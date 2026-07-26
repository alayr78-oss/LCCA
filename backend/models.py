from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -----------------------------------------
# User Management
# -----------------------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(50), default="Researcher") # Administrator, Researcher, Engineer, Inspector
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------------------
# Country Profile Framework
# -----------------------------------------
class CountryProfile(db.Model):
    __tablename__ = 'country_profiles'
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100), unique=True, nullable=False)
    currency = db.Column(db.String(10))
    labour_cost_factor = db.Column(db.Float, default=1.0)
    material_cost_factor = db.Column(db.Float, default=1.0)
    inflation_rate = db.Column(db.Float, default=0.02)
    maintenance_availability = db.Column(db.String(100))
    rehab_delay_factor = db.Column(db.Float, default=1.0)

# -----------------------------------------
# Core Project
# -----------------------------------------
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country_profiles.id'))
    track_length_km = db.Column(db.Float)
    railway_type = db.Column(db.String(100))
    traffic_level = db.Column(db.String(100))
    axle_load_tonnes = db.Column(db.Float)
    climate_condition = db.Column(db.String(100))
    analysis_period_years = db.Column(db.Integer, default=50)
    discount_rate = db.Column(db.Float, default=0.08)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    country = db.relationship('CountryProfile')

# -----------------------------------------
# Component & Material Library
# -----------------------------------------
class Component(db.Model):
    __tablename__ = 'components'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # e.g., Rails, Sleepers, Ballast
    description = db.Column(db.Text)

class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'))
    
    expected_life = db.Column(db.Float)
    initial_cost = db.Column(db.Float)
    maintenance_cost = db.Column(db.Float)
    replacement_cycle = db.Column(db.Float)
    deterioration_behaviour = db.Column(db.String(255))
    carbon_footprint = db.Column(db.Float)
    embodied_energy = db.Column(db.Float)
    
    component = db.relationship('Component')

# -----------------------------------------
# Asset Database
# -----------------------------------------
class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    
    location_start_km = db.Column(db.Float) # Chainage
    location_end_km = db.Column(db.Float)
    latitude = db.Column(db.Float) # Future GIS
    longitude = db.Column(db.Float)
    
    install_year = db.Column(db.Integer)
    # Note: Current condition, remaining service life, and risk are calculated by engines 
    # based on InspectionHistory, age, and Knowledge parameters, not stored directly here.

    project = db.relationship('Project', backref='assets')
    component = db.relationship('Component')
    material = db.relationship('Material')

# -----------------------------------------
# History & Condition Data
# -----------------------------------------
class InspectionHistory(db.Model):
    __tablename__ = 'inspection_history'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    inspection_date = db.Column(db.Date)
    component = db.Column(db.String(100)) # e.g. Rails, Sleepers
    location = db.Column(db.String(100))
    inspector = db.Column(db.String(100))
    inspection_method = db.Column(db.String(100))
    condition_rating = db.Column(db.Float) # Observed condition
    defect_type = db.Column(db.String(255))
    defect_severity = db.Column(db.String(100))
    maintenance_action = db.Column(db.String(255))
    observation = db.Column(db.Text)
    document_reference = db.Column(db.String(255))
    
    asset = db.relationship('Asset', backref='inspections')

class MaintenanceHistory(db.Model):
    __tablename__ = 'maintenance_history'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    maintenance_date = db.Column(db.Date)
    maintenance_type = db.Column(db.String(100))
    maintenance_action = db.Column(db.String(255))
    
    cost = db.Column(db.Float)
    labour_cost = db.Column(db.Float)
    material_cost = db.Column(db.Float)
    duration_days = db.Column(db.Float)
    
    before_condition = db.Column(db.Float)
    after_condition = db.Column(db.Float)
    
    asset = db.relationship('Asset', backref='maintenance_records')

# -----------------------------------------
# Engineering Knowledge & Reference Base
# -----------------------------------------
class Reference(db.Model):
    __tablename__ = 'references'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255))
    year = db.Column(db.Integer)
    publication = db.Column(db.String(255)) # Standard/Journal/Manual
    source = db.Column(db.String(255))
    url_doi = db.Column(db.String(255))
    parameter_supported = db.Column(db.String(255))

class KnowledgeParameter(db.Model):
    __tablename__ = 'knowledge_parameters'
    id = db.Column(db.Integer, primary_key=True)
    parameter_category = db.Column(db.String(100)) # Technical, Economic, Environmental, Condition_Weight
    parameter_name = db.Column(db.String(255))
    component_type = db.Column(db.String(100)) # e.g., 'Sleepers', 'Rails'
    default_value = db.Column(db.Float)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    user_value = db.Column(db.Float)
    assumption = db.Column(db.Text)
    is_editable = db.Column(db.Boolean, default=True)
    
    reference_id = db.Column(db.Integer, db.ForeignKey('references.id'))
    reference = db.relationship('Reference')

class FailureMode(db.Model):
    __tablename__ = 'failure_modes'
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'))
    mechanism = db.Column(db.String(255)) # e.g., cracking, fouling
    description = db.Column(db.Text)
    severity_level = db.Column(db.String(50))
    probability = db.Column(db.Float)
    consequence = db.Column(db.Float)
    recommended_treatment = db.Column(db.String(255))
    
    component = db.relationship('Component')

class MaintenanceStrategy(db.Model):
    __tablename__ = 'maintenance_strategies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'))
    interval_years = db.Column(db.Float)
    expected_life_improvement = db.Column(db.Float)
    cost_impact = db.Column(db.Float)
    
    component = db.relationship('Component')

# -----------------------------------------
# Scenario Management
# -----------------------------------------
class Scenario(db.Model):
    __tablename__ = 'scenarios'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    name = db.Column(db.String(255), nullable=False)
    
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    maintenance_strategy_id = db.Column(db.Integer, db.ForeignKey('maintenance_strategies.id'))
    country_profile_id = db.Column(db.Integer, db.ForeignKey('country_profiles.id'))
    
    discount_rate = db.Column(db.Float)
    analysis_period = db.Column(db.Integer)
    cost_assumptions = db.Column(db.Text)
    
    project = db.relationship('Project', backref='scenarios')
    material = db.relationship('Material')
    strategy = db.relationship('MaintenanceStrategy')
    country = db.relationship('CountryProfile')

# -----------------------------------------
# Phase 5: Advanced Decision Support Engine
# -----------------------------------------
class DecisionCriteria(db.Model):
    __tablename__ = 'decision_criteria'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # e.g. Lifecycle Cost, Risk Score
    category = db.Column(db.String(50)) # Economic, Technical, Safety, Environmental, Operational
    description = db.Column(db.Text)

class CriteriaWeight(db.Model):
    __tablename__ = 'criteria_weights'
    id = db.Column(db.Integer, primary_key=True)
    criteria_id = db.Column(db.Integer, db.ForeignKey('decision_criteria.id'))
    weight_type = db.Column(db.String(50)) # e.g., 'Default', 'User-defined', 'AHP'
    weight_value = db.Column(db.Float, nullable=False)
    source_reference = db.Column(db.String(255))
    assumption = db.Column(db.Text)

class AlternativeStrategy(db.Model):
    __tablename__ = 'alternative_strategies'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    name = db.Column(db.String(255), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    maintenance_strategy_id = db.Column(db.Integer, db.ForeignKey('maintenance_strategies.id'))

class DecisionResult(db.Model):
    __tablename__ = 'decision_results'
    id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(db.Integer, db.ForeignKey('alternative_strategies.id'))
    overall_score = db.Column(db.Float)
    lifecycle_cost = db.Column(db.Float)
    risk_score = db.Column(db.Float)
    reliability_score = db.Column(db.Float)
    carbon_footprint = db.Column(db.Float)
    
class RecommendationHistory(db.Model):
    __tablename__ = 'recommendation_history'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    recommended_alternative_id = db.Column(db.Integer, db.ForeignKey('alternative_strategies.id'))
    date_generated = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_level = db.Column(db.Float)
    reasons = db.Column(db.Text) # JSON string of explanation

# -----------------------------------------
# Phase 6: Visualization & Validation
# -----------------------------------------
class ValidationResult(db.Model):
    __tablename__ = 'validation_results'
    id = db.Column(db.Integer, primary_key=True)
    case_study_id = db.Column(db.Integer, db.ForeignKey('case_study_snapshots.id'))
    validation_type = db.Column(db.String(100)) # Mathematical, Model, Sensitivity, Expert
    dataset_used = db.Column(db.String(255))
    metric = db.Column(db.String(100)) # e.g. NPV error, RMSE, Parameter Tested
    result_value = db.Column(db.Text) # String to store various formats (e.g. '0.4%', 'High Impact')
    date_run = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.Column(db.Text)

class CaseStudySnapshot(db.Model):
    __tablename__ = 'case_study_snapshots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    input_dataset_json = db.Column(db.Text)
    country_profile_json = db.Column(db.Text)
    material_selection_json = db.Column(db.Text)
    condition_parameters_json = db.Column(db.Text)
    lcca_assumptions_json = db.Column(db.Text)
    risk_weights_json = db.Column(db.Text)
    mcdm_weights_json = db.Column(db.Text)
    selected_models_json = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------------------
# Phase 7: GIS & Digital Twin Hooks
# -----------------------------------------
class SpatialGeometry(db.Model):
    """ Future GIS-based Asset Visualization Framework """
    __tablename__ = 'spatial_geometries'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    geometry_type = db.Column(db.String(50)) # Point, LineString, Polygon
    coordinates_json = db.Column(db.Text)
    srid = db.Column(db.Integer, default=4326) # Spatial Reference System Identifier
    alignment_reference = db.Column(db.String(100))

class SensorStream(db.Model):
    """ Architecture hook for future Digital Twin IoT integration """
    __tablename__ = 'sensor_streams'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    sensor_type = db.Column(db.String(100)) # e.g. Accelerometer, Strain Gauge
    data_frequency = db.Column(db.String(50))
    last_payload_json = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    
class DroneInspection(db.Model):
    """ Architecture hook for drone/point-cloud condition updates """
    __tablename__ = 'drone_inspections'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    flight_date = db.Column(db.Date)
    point_cloud_url = db.Column(db.String(255))
    ai_detected_defects_json = db.Column(db.Text)
