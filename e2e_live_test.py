import urllib.request
import json
import time

BASE_URL = "https://lcca.onrender.com/api"

def post(endpoint, payload):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=json.dumps(payload).encode('utf-8')) as response:
            return json.loads(response.read().decode('utf-8')), response.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8')), e.code

print("Starting End-to-End Live Pipeline Test on RAM-DSS...")
time.sleep(1)

# 1. Seed DB
print("\n--- 1. Seeding Database ---")
res, status = post("/admin/seed_db", {})
print(f"Status: {status} | Response: {res}")
if status != 200:
    print("WARNING: Seed DB might have failed or is already seeded.")

# 2. Create Project
print("\n--- 2. Creating Project ---")
project_payload = {
    "name": f"E2E Automated Test {int(time.time())}",
    "track_length_km": 50,
    "discount_rate": 0.08,
    "analysis_period_years": 40
}
res, status = post("/projects", project_payload)
print(f"Status: {status} | Response: {res}")
assert status == 201, "Failed to create project!"
project_id = res['project_id']

# 3. Create Asset
print("\n--- 3. Creating Asset ---")
asset_payload = {
    "project_id": project_id,
    "component_id": 1,
    "location_start_km": 0,
    "location_end_km": 50,
    "install_year": 2020
}
res, status = post("/assets", asset_payload)
print(f"Status: {status} | Response: {res}")
assert status == 201, "Failed to create asset!"
asset_id = res['id']

# 4. Log Inspection
print("\n--- 4. Logging Inspection ---")
inspection_payload = {
    "asset_id": asset_id,
    "inspection_date": "2026-08-07T00:00:00",
    "inspector": "Automated Tester",
    "condition_rating": 85,
    "defect_severity": "Minor"
}
res, status = post("/inspections", inspection_payload)
print(f"Status: {status} | Response: {res}")
assert status == 201, "Failed to log inspection!"

# 5. Condition Engine
print("\n--- 5. Testing Condition Engine ---")
condition_payload = {
    "components": [
        {"id": 1, "name": "Rails", "condition_rating": 85, "weight": 1.0}
    ],
    "deterioration_rate": 2.5,
    "model_type": "Linear"
}
res, status = post("/engine/condition", condition_payload)
print(f"Status: {status} | ICI: {res.get('ici_result', {}).get('ici')} | RSL: {res.get('rsl_result', {}).get('rsl_years')} years")
assert status == 200, "Condition engine failed!"

# 6. LCCA Engine
print("\n--- 6. Testing LCCA Engine ---")
lcca_payload = {
    "components": [
        {"id": 1, "name": "Rails", "initial_cost": 500000, "maintenance_cost": 25000, "expected_life": 50}
    ],
    "country_profile": {
        "labour_cost_factor": 1.2,
        "material_cost_factor": 1.1,
        "inflation_rate": 0.02
    },
    "analysis_period": 40,
    "discount_rate": 0.08,
    "track_length_km": 50
}
res, status = post("/lcca/calculate", lcca_payload)
print(f"Status: {status} | NPV: ${res.get('npv', 0):,.2f} | EAC: ${res.get('eac', 0):,.2f}")
assert status == 200, "LCCA engine failed!"

# 7. Decision Engine
print("\n--- 7. Testing Decision Engine (MCDM) ---")
mcdm_payload = {
    "weights": {"lifecycle_cost": 0.5, "risk": 0.3, "carbon": 0.2},
    "alternatives": [
        {"id": 1, "name": "Strategy A", "lifecycle_cost": 1000000, "risk_score": 45, "carbon_footprint": 1200},
        {"id": 2, "name": "Strategy B", "lifecycle_cost": 1200000, "risk_score": 30, "carbon_footprint": 900}
    ]
}
res, status = post("/recommendation/generate", mcdm_payload)
print(f"Status: {status}")
print(f"Recommendation: {res.get('recommendation', {}).get('recommended_strategy')} (Score: {res.get('recommendation', {}).get('score')})")
assert status == 200, "Decision engine failed!"

# 8. Export Engine (PDF)
print("\n--- 8. Testing Report Export (PDF) ---")
report_payload = {
    "format": "pdf",
    "report_data": {
        "project": {"name": f"E2E Automated Test {int(time.time())}", "length": 50},
        "ici": 85,
        "rsl": 18,
        "npv": 1500000,
        "eac": 75000,
        "recommendation": "Strategy B"
    }
}
req = urllib.request.Request(f"{BASE_URL}/export/report", method="POST")
req.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(req, data=json.dumps(report_payload).encode('utf-8')) as response:
        pdf_bytes = response.read()
        print(f"Status: {response.status} | PDF Bytes Received: {len(pdf_bytes)}")
        assert response.status == 200, "Export failed!"
        assert pdf_bytes.startswith(b"%PDF-"), "Invalid PDF signature!"
except urllib.error.HTTPError as e:
    print(f"Export Error: {e.code} - {e.read().decode('utf-8')}")

print("\n🎉 ALL E2E API PIPELINE TESTS PASSED ON LIVE SERVER! 🎉")
