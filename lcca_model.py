# lcca_model.py
# Life Cycle Cost Analysis (LCCA) model for multiple Railway Infrastructure Scenarios
# All monetary values in Pakistani Rupees (Rs)

from typing import List, Dict, Any, Tuple

# ─── Global Constants & Defaults ───────────────────────────────────────────────

DEFAULTS: Dict = {
    "scenario_id": "sleepers", # 'sleepers', 'joints', 'track_system'
    "track_length_km": 44,
    "gauge_width": 1676,
    "discount_rate": 0.08,
    "target_years": "10, 25, 50",
    "model_mode": "scenario",
    
    # scenario_id='sleepers' (S1)
    "wooden_sleeper_cost": 600,
    "concrete_sleeper_cost": 960,
    "wooden_sleeper_x": 2,
    "concrete_sleeper_per_rail": 14,
    "wooden_maint_rate": 0.08,
    "concrete_maint_rate": 0.03,
    "wooden_lifespan": 25,
    "concrete_lifespan": 50,
    
    # scenario_id='joints' (S2)
    "weld_joint_cost": 5000,
    "fishplate_cost": 2310,
    "fishplates_per_joint": 2,
    "joint_spacing_m": 12.5,
    "weld_freq_per_km": 160,
    "weld_maint_rate": 0.03,
    "fishplate_maint_rate": 0.08,
    "weld_lifespan": 50,
    "fishplate_lifespan": 10,
    
    # scenario_id='track_system' (S3) Ballasted vs Slab
    "ballast_depth_mm": 250,
    "shoulder_width_mm": 500,
    "ballast_cost_per_cft": 120,
    "slab_ic_per_m": 20658, # 1.3x ballasted as per ratio method in Scenario 3 txt
    "ballasted_maint_rate": 0.05,
    "slab_maint_rate": 0.015,
    "ballasted_lifespan": 12.5,
    "slab_lifespan": 80,
}

# ─── Financial Formulas ─────────────────────────────────────────────────────────

def capital_recovery_factor(r: float, n: int) -> float:
    if r <= 0: return 1 / n
    return r * (1 + r) ** n / ((1 + r) ** n - 1)

# ─── Core Calculation Engine ────────────────────────────────────────────────────

def calculate_option_results(
    ic: float,
    maint_rate: float,
    lifespan: float,
    repl_rate: float,
    analysis_years: List[int],
    r: float,
    mode: str,
    scenario_id: str
) -> Dict[int, Dict[str, float]]:
    
    annual_maint = ic * maint_rate
    repl_cost_per_event = ic * repl_rate
    
    results = {}
    for n in analysis_years:
        # 1. NPV Maintenance (Ordinary Annuity formula)
        npv_m = annual_maint * ((1 - (1 + r) ** -n) / r)
        
        # 2. NPV Replacement (Discrete events, include end of period if k <= n)
        npv_repl = 0
        k = lifespan
        while k <= n:
            npv_repl += repl_cost_per_event / ((1 + r) ** k)
            k += lifespan
                    
        # 3. LCC Calculation
        lcc = ic + npv_m + npv_repl
        
        # 4. CRF Calculation
        crf = capital_recovery_factor(r, n)
        
        # 5. EAC Calculation
        eac = lcc * crf
        
        results[n] = {
            "initial_cost": ic,
            "annual_maintenance": annual_maint,
            "npv_maintenance": npv_m,
            "npv_replacement": npv_repl,
            "lcc": lcc,
            "crf": crf,
            "eac": eac,
        }
    return results

# ─── Parameter Orchestration ────────────────────────────────────────────────────

def run_lcca(form_data: Dict) -> Dict:
    # 1. Merge form with defaults
    p = {**DEFAULTS}
    for k, v in form_data.items():
        if v != "" and v is not None:
            p[k] = v
            
    # 2. Type conversion and scaling
    p["track_length_km"] = float(p["track_length_km"])
    p["gauge_width"] = float(p.get("gauge_width", 1676))
    p["discount_rate"] = float(p["discount_rate"])
    if p["discount_rate"] > 1: p["discount_rate"] /= 100.0
    
    # Apply Parameter Sensitivity and RCM
    p["env_factor"] = float(p.get("env_factor", 1.0))
    p["sensitivity"] = float(p.get("sensitivity", 0.0))
    p["rcm_mode"] = p.get("rcm_mode", "proactive")
    
    p["discount_rate"] += p["sensitivity"]
    
    # Scale all maintenance rates
    for k in p:
        if "maint_rate" in k:
            val = float(p[k])
            if val > 1: val /= 100.0
            
            # Apply Environment Factor
            if "wooden" in k or "ballasted" in k:
                val *= p["env_factor"] # Only weak elements are heavily degraded
            elif p["env_factor"] > 1.0:
                val *= 1.1 # Concrete slightly degraded by severe environments
                
            # Apply RCM
            if p["rcm_mode"] == "reactive":
                val *= 1.20 # 20% penalty for reactive breakdown maintenance
                
            p[k] = val
            
    try:
        years = sorted([int(x.strip()) for x in str(p["target_years"]).split(",") if x.strip()])
    except:
        years = [10, 25, 50]
    p["analysis_years"] = years
    
    sid = p["scenario_id"]
    r = p["discount_rate"]
    mode = p["model_mode"]
    
    titles = {
        "sleepers": ("Hardwood Timber", "Pre-stressed Concrete"),
        "joints": ("Jointed Track", "Thermit Welding"),
        "track_system": ("Ballast Track", "Slab Track")
    }
    opt_a_name, opt_b_name = titles.get(sid, ("Option A", "Option B"))
    
    # 3. Calculate ICs based on Scenario
    if sid == "sleepers":
        # Using legacy quantities
        rail_len = 0.00381
        ibeams = int(-(-p["track_length_km"] // rail_len))
        
        # Calculate sleepers per rail
        m_val = 12.5
        wood_x = float(p.get("wooden_sleeper_x", 2))
        wooden_per_rail = int(m_val + wood_x + 0.5) # Equivalent to ceil for x.5 cases like 14.5 -> 15
        
        ic_a = (ibeams * wooden_per_rail) * float(p["wooden_sleeper_cost"])
        
        concrete_per_rail = float(p.get("concrete_sleeper_per_rail", 14))
        ic_b = (ibeams * concrete_per_rail) * float(p["concrete_sleeper_cost"])
        
        maint_a, maint_b = float(p["wooden_maint_rate"]), float(p["concrete_maint_rate"])
        life_a, life_b = float(p["wooden_lifespan"]), float(p["concrete_lifespan"])
        repl_a, repl_b = 0.40, 0.40
        
    elif sid == "joints":
        joint_spacing_km = float(p.get("joint_spacing_m", 12.5)) / 1000.0
        ibeams = int(-(-p["track_length_km"] // joint_spacing_km)) if joint_spacing_km > 0 else 0
        num_joints = max(0, (ibeams - 1) * 2)
        
        plates_per_joint = float(p.get("fishplates_per_joint", 2))
        ic_a = (num_joints * plates_per_joint) * float(p["fishplate_cost"])
        
        weld_freq = float(p.get("weld_freq_per_km", 160))
        num_weld_joints = p["track_length_km"] * weld_freq
        ic_b = num_weld_joints * float(p["weld_joint_cost"])
        
        maint_a, maint_b = float(p["fishplate_maint_rate"]), float(p["weld_maint_rate"])
        life_a, life_b = float(p["fishplate_lifespan"]), float(p["weld_lifespan"])
        repl_a, repl_b = 0.40, 0.40
        
    else: # track_system
        length_m = p["track_length_km"] * 1000
        
        gauge_width_mm = float(p.get("gauge_width", 1676))
        ballast_depth_mm = float(p.get("ballast_depth_mm", 250))
        shoulder_width_mm = float(p.get("shoulder_width_mm", 500))
        cost_per_cft = float(p.get("ballast_cost_per_cft", 120))
        
        bed_width_mm = gauge_width_mm + (2 * shoulder_width_mm)
        area_sq_m = (bed_width_mm / 1000.0) * (ballast_depth_mm / 1000.0)
        volume_cu_m = area_sq_m * length_m
        volume_cu_ft = volume_cu_m * 35.3147
        
        ic_a = volume_cu_ft * cost_per_cft
        ic_b = length_m * float(p["slab_ic_per_m"])
        
        maint_a, maint_b = float(p["ballasted_maint_rate"]), float(p["slab_maint_rate"])
        life_a, life_b = float(p["ballasted_lifespan"]), float(p["slab_lifespan"])
        repl_a, repl_b = 0.40, 0.40

    # 4. Run Analysis
    res_a = calculate_option_results(ic_a, maint_a, life_a, repl_a, years, r, mode, sid)
    res_b = calculate_option_results(ic_b, maint_b, life_b, repl_b, years, r, mode, sid)
    
    # 5. Generate Time Series for Graphs (Year-by-Year Cash Flows)
    max_yr = max(years)
    labels = list(range(max_yr + 1))
    flow_a = {"maint": [], "repl": []}
    flow_b = {"maint": [], "repl": []}
    for t in labels:
        if t == 0:
            flow_a["maint"].append(0); flow_a["repl"].append(ic_a)
            flow_b["maint"].append(0); flow_b["repl"].append(ic_b)
        else:
            ma = ic_a * maint_a
            mb = ic_b * maint_b
            
            ra = 0
            k_a = life_a
            while round(k_a) <= t:
                if round(k_a) == t:
                    ra += ic_a * repl_a
                k_a += life_a
                
            rb = 0
            k_b = life_b
            while round(k_b) <= t:
                if round(k_b) == t:
                    rb += ic_b * repl_b
                k_b += life_b
            
            flow_a["maint"].append(ma)
            flow_a["repl"].append(ra)
            flow_b["maint"].append(mb)
            flow_b["repl"].append(rb)

    return {
        "params": p,
        "opt_a_name": opt_a_name,
        "opt_b_name": opt_b_name,
        "results_a": res_a,
        "results_b": res_b,
        "cash_flow": {
            "labels": labels,
            "a": flow_a,
            "b": flow_b
        }
    }
