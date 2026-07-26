from app import app, db
from models import Project, Material, Asset

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Seeding materials...")
        materials = [
            Material(
                name="Hardwood Timber Sleeper",
                category="Sleeper",
                service_life_years=25,
                deterioration_rate=0.08,
                failure_probability=0.1,
                maint_interval_years=2.0,
                initial_cost=600,
                routine_maint_cost=48,
                rehab_cost=200,
                replacement_cost=240,
                salvage_value=50,
                carbon_emission_kg=15.0,
                embodied_energy_mj=100.0
            ),
            Material(
                name="Pre-stressed Concrete Sleeper",
                category="Sleeper",
                service_life_years=50,
                deterioration_rate=0.03,
                failure_probability=0.05,
                maint_interval_years=5.0,
                initial_cost=960,
                routine_maint_cost=28.8,
                rehab_cost=150,
                replacement_cost=384,
                salvage_value=0,
                carbon_emission_kg=35.0,
                embodied_energy_mj=250.0
            ),
            Material(
                name="Steel Sleeper",
                category="Sleeper",
                service_life_years=40,
                deterioration_rate=0.04,
                failure_probability=0.06,
                maint_interval_years=4.0,
                initial_cost=1200,
                routine_maint_cost=40,
                rehab_cost=180,
                replacement_cost=480,
                salvage_value=100,
                carbon_emission_kg=45.0,
                embodied_energy_mj=300.0
            ),
            Material(
                name="Composite Polymeric Sleeper",
                category="Sleeper",
                service_life_years=50,
                deterioration_rate=0.02,
                failure_probability=0.03,
                maint_interval_years=10.0,
                initial_cost=1500,
                routine_maint_cost=20,
                rehab_cost=100,
                replacement_cost=600,
                salvage_value=0,
                carbon_emission_kg=25.0,
                embodied_energy_mj=180.0
            )
        ]
        
        db.session.bulk_save_objects(materials)

        print("Seeding projects...")
        p1 = Project(
            name="Main Line Karachi-Lahore Sector 1",
            country="Pakistan",
            track_length_km=44.0,
            railway_type="Heavy Haul",
            traffic_level="High",
            axle_load_tonnes=25.0,
            climate_condition="Arid",
            analysis_period_years=50,
            discount_rate=0.08,
            inflation_rate=0.02,
            currency="PKR"
        )
        db.session.add(p1)
        
        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed_data()
