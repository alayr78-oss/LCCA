"""lcca_model.py

Life cycle cost engine of the Railway LCCA Calculator (Karachi Circular Railway).

Three scenarios compare two track options each:
    sleepers      : hardwood timber (A) vs pre-stressed concrete (B)
    joints        : fishplate jointed track (A) vs thermit welded track (B)
    track_system  : ballast (A) vs slab track (B)

For each option and each analysis period n:
    PV_maintenance = A * (1 - (1 + r)^-n) / r             (ordinary annuity, A = m * IC)
    PV_replacement = sum over replacement years t of  rho * IC / (1 + r)^t
    LCC            = IC + PV_maintenance + PV_replacement
    EAC            = LCC * CRF,   CRF = r (1 + r)^n / ((1 + r)^n - 1)

All amounts are in Pakistani rupees at constant prices.
"""
import math
import re
from typing import Dict, List

VERSION = "2.0"
FT3_PER_M3 = 35.3147

# Defaults. Percentages are stored as fractions; the form shows them x100.
DEFAULTS: Dict = {
    # geometry
    "track_length_km": 44.0,
    "number_of_tracks": 2,
    "rail_length_m": 12.5,
    "gauge_width": 1676,
    # economics
    "discount_rate": 0.08,
    "target_years": "10, 25, 50",
    "replacement_rate": 0.40,
    # scenario 1: sleepers
    "wooden_sleeper_cost": 600,
    "wooden_sleeper_x": 2,
    "wooden_maint_rate": 0.08,
    "wooden_life": 10,
    "concrete_sleeper_cost": 960,
    "concrete_sleeper_per_rail": 14,
    "concrete_maint_rate": 0.03,
    "concrete_life": 35,
    # scenario 2: joints
    "fishplate_cost": 2310,
    "fishplates_per_joint": 2,
    "fishplate_maint_rate": 0.08,
    "fishplate_life": 10,
    "weld_joint_cost": 5000,
    "weld_freq_per_km": 160,
    "weld_maint_rate": 0.03,
    "weld_life": 50,
    # scenario 3: track system
    "ballast_depth_mm": 250,
    "shoulder_width_mm": 500,
    "ballast_cost_per_cft": 105,
    "ballasted_maint_rate": 0.05,
    "ballast_life": 12.5,
    "slab_ic_per_m": 20658,
    "slab_maint_rate": 0.015,
    "slab_life": 80,
}

SCENARIOS = {
    "sleepers": ("Hardwood Timber", "Pre-stressed Concrete"),
    "joints": ("Jointed Track", "Thermit Welding"),
    "track_system": ("Ballast Track", "Slab Track"),
}

# Options that take the full environmental factor. All others take +10 % when the factor is above 1.
FULL_ENV_OPTIONS = {"wooden", "ballast"}
REACTIVE_MULTIPLIER = 1.2
OTHER_ENV_MULTIPLIER = 1.1


class InputError(ValueError):
    """Raised when form input is invalid. `errors` holds user-readable messages."""

    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


# ----------------------------------------------------------------------------
# Financial functions
# ----------------------------------------------------------------------------
def annuity_factor(r: float, n: int) -> float:
    """Present value of 1 paid at the end of each of n years."""
    return float(n) if r == 0 else (1 - (1 + r) ** (-n)) / r


def capital_recovery_factor(r: float, n: int) -> float:
    return 1.0 / n if r == 0 else r * (1 + r) ** n / ((1 + r) ** n - 1)


def replacement_years(life: float, n: int, include_end: bool = False) -> List[float]:
    """Times (in years, possibly fractional) at which the component reaches the end of its life
    within the analysis period n. Replacements are discounted at their exact time.

    A replacement that falls exactly at the end of the analysis period is not
    charged unless include_end is True.
    """
    times, k = [], 1
    while True:
        t = k * life
        if t > n + 1e-9 or (abs(t - n) < 1e-9 and not include_end):
            break
        times.append(t)
        k += 1
    return times


def analyse_option(ic: float, annual_maint: float, life: float, repl_rate: float,
                   r: float, horizons: List[int], include_end: bool = False) -> Dict[int, Dict]:
    """Life cycle cost of one option for every analysis period."""
    out = {}
    for n in horizons:
        pv_m = annual_maint * annuity_factor(r, n)
        ys = replacement_years(life, n, include_end)
        pv_r = sum(repl_rate * ic / (1 + r) ** t for t in ys)
        lcc = ic + pv_m + pv_r
        crf = capital_recovery_factor(r, n)
        out[n] = {
            "initial_cost": ic,
            "annual_maintenance": annual_maint,
            "npv_maintenance": pv_m,
            "npv_replacement": pv_r,
            "num_replacements": len(ys),
            "replacement_years": ys,
            "lcc": lcc,
            "crf": crf,
            "eac": lcc * crf,
        }
    return out


def maintenance_multiplier(option_key: str, rcm_mode: str, env_factor: float) -> float:
    rcm = REACTIVE_MULTIPLIER if rcm_mode == "reactive" else 1.0
    if option_key in FULL_ENV_OPTIONS:
        env = env_factor
    else:
        env = OTHER_ENV_MULTIPLIER if env_factor > 1 else 1.0
    return rcm * env


# ----------------------------------------------------------------------------
# Quantities
# ----------------------------------------------------------------------------
def panels_per_track(length_km: float, rail_length_m: float) -> int:
    return math.ceil(round(length_km * 1000.0 / rail_length_m, 9))


def quantities(p: Dict) -> Dict:
    length_m = p["track_length_km"] * 1000.0
    tracks = p["number_of_tracks"]
    panels = panels_per_track(p["track_length_km"], p["rail_length_m"])
    q = {"panels_per_track": panels}

    # scenario 1: sleepers (wooden count follows the M + X rule, M = rail length in metres)
    wood_per_rail = math.floor(p["rail_length_m"] + p["wooden_sleeper_x"] + 0.5)
    q["wooden_per_rail"] = wood_per_rail
    q["wooden_count"] = panels * wood_per_rail * tracks
    q["concrete_count"] = panels * p["concrete_sleeper_per_rail"] * tracks

    # scenario 2: joints (two rails per track)
    q["joints"] = max(0, panels - 1) * 2 * tracks
    q["fishplates"] = q["joints"] * p["fishplates_per_joint"]
    q["welds"] = math.ceil(round(p["track_length_km"] * p["weld_freq_per_km"] * tracks, 9))

    # scenario 3: track system
    bed_width_m = (p["gauge_width"] + 2 * p["shoulder_width_mm"]) / 1000.0
    q["ballast_m3"] = bed_width_m * (p["ballast_depth_mm"] / 1000.0) * length_m * tracks
    q["slab_length_m"] = length_m * tracks
    return q


# ----------------------------------------------------------------------------
# Input handling
# ----------------------------------------------------------------------------
_RULES = {
    # key: (label, min, max, kind)   kind: "pct" percent in form, "int", "num"
    "track_length_km": ("Route kilometres", 0.1, 1000, "num"),
    "number_of_tracks": ("Number of tracks", 1, 4, "int"),
    "rail_length_m": ("Rail panel length (m)", 1, 30, "num"),
    "gauge_width": ("Gauge width (mm)", 500, 3000, "num"),
    "discount_rate": ("Discount rate (%)", 0, 50, "pct"),
    "replacement_rate": ("Replacement cost (% of initial cost)", 0, 200, "pct"),
    "wooden_sleeper_cost": ("Wooden sleeper cost", 0, 1e9, "num"),
    "wooden_sleeper_x": ("Wooden sleeper X value", 1, 4, "num"),
    "wooden_maint_rate": ("Wooden maintenance rate (%)", 0, 100, "pct"),
    "wooden_life": ("Wooden sleeper service life (years)", 1, 200, "num"),
    "concrete_sleeper_cost": ("PSC sleeper cost", 0, 1e9, "num"),
    "concrete_sleeper_per_rail": ("PSC sleepers per rail", 1, 50, "int"),
    "concrete_maint_rate": ("PSC maintenance rate (%)", 0, 100, "pct"),
    "concrete_life": ("PSC sleeper service life (years)", 1, 200, "num"),
    "fishplate_cost": ("Fishplate cost", 0, 1e9, "num"),
    "fishplates_per_joint": ("Plates per joint", 1, 8, "int"),
    "fishplate_maint_rate": ("Fishplate maintenance rate (%)", 0, 100, "pct"),
    "fishplate_life": ("Fishplate service life (years)", 1, 200, "num"),
    "weld_joint_cost": ("Weld joint cost", 0, 1e9, "num"),
    "weld_freq_per_km": ("Weld frequency (joints per km)", 0, 1000, "num"),
    "weld_maint_rate": ("Weld maintenance rate (%)", 0, 100, "pct"),
    "weld_life": ("Weld service life (years)", 1, 200, "num"),
    "ballast_depth_mm": ("Ballast depth (mm)", 50, 1000, "num"),
    "shoulder_width_mm": ("Shoulder width (mm)", 0, 2000, "num"),
    "ballast_cost_per_cft": ("Ballast cost (Rs/ft3)", 0, 1e6, "num"),
    "ballasted_maint_rate": ("Ballast maintenance rate (%)", 0, 100, "pct"),
    "ballast_life": ("Ballast service life (years)", 1, 200, "num"),
    "slab_ic_per_m": ("Slab cost per metre", 0, 1e9, "num"),
    "slab_maint_rate": ("Slab maintenance rate (%)", 0, 100, "pct"),
    "slab_life": ("Slab service life (years)", 1, 200, "num"),
}


def parse_horizons(text) -> List[int]:
    tokens = re.findall(r"[^\s,;]+", str(text))
    if not tokens:
        raise InputError(["Analysis periods: enter at least one value, for example 10, 25, 50."])
    years = []
    for tok in tokens:
        if not re.fullmatch(r"\d+", tok) or not (1 <= int(tok) <= 100):
            raise InputError([f"Analysis periods: '{tok}' is not a whole number between 1 and 100."])
        years.append(int(tok))
    years = sorted(set(years))
    if len(years) > 6:
        raise InputError(["Analysis periods: use at most six values."])
    return years


def build_params(form: Dict) -> Dict:
    """Merge form input with defaults and validate. Empty fields fall back to the default."""
    errors, p = [], {}
    for key, (label, lo, hi, kind) in _RULES.items():
        raw = form.get(key, "")
        raw = "" if raw is None else str(raw).strip()
        if raw == "":
            p[key] = DEFAULTS[key]
            continue
        try:
            val = float(raw)
        except ValueError:
            errors.append(f"{label}: '{raw}' is not a number.")
            continue
        if not math.isfinite(val):
            errors.append(f"{label}: '{raw}' is not a valid number.")
            continue
        if kind == "int" and val != int(val):
            errors.append(f"{label}: must be a whole number.")
            continue
        if not (lo <= val <= hi):
            errors.append(f"{label}: must be between {lo:g} and {hi:g}.")
            continue
        p[key] = val / 100.0 if kind == "pct" else (int(val) if kind == "int" else val)

    scenario = str(form.get("scenario_id", "sleepers") or "sleepers")
    if scenario not in SCENARIOS:
        errors.append(f"Scenario: '{scenario}' is not available.")
    rcm = str(form.get("rcm_mode", "proactive") or "proactive")
    if rcm not in ("proactive", "reactive"):
        errors.append("Maintenance strategy must be proactive or reactive.")
    try:
        env = float(form.get("env_factor", 1.0) or 1.0)
        if not (1.0 <= env <= 3.0):
            raise ValueError
    except ValueError:
        errors.append("Environmental factor must be between 1.0 and 3.0.")
        env = 1.0
    try:
        sens = float(form.get("sensitivity", 0) or 0)
        if not (-0.5 <= sens <= 0.5):
            raise ValueError
    except ValueError:
        errors.append("Sensitivity must be between -0.5 and +0.5.")
        sens = 0.0
    try:
        horizons = parse_horizons(form.get("target_years", "") or DEFAULTS["target_years"])
    except InputError as e:
        errors.extend(e.errors)
        horizons = []

    if errors:
        raise InputError(errors)

    p.update({
        "scenario_id": scenario,
        "model_mode": rcm,
        "env_factor": env,
        "sensitivity": sens,
        "analysis_years": horizons,
        "base_discount_rate": p["discount_rate"],
        # sensitivity is relative: +0.1 means the rate is multiplied by 1.10
        "discount_rate": p["discount_rate"] * (1.0 + sens),
    })
    return p


# ----------------------------------------------------------------------------
# Scenario set-up and main entry point
# ----------------------------------------------------------------------------
def _options(p: Dict, q: Dict):
    s = p["scenario_id"]
    if s == "sleepers":
        return [
            dict(key="wooden", ic=q["wooden_count"] * p["wooden_sleeper_cost"], m=p["wooden_maint_rate"], life=p["wooden_life"]),
            dict(key="concrete", ic=q["concrete_count"] * p["concrete_sleeper_cost"], m=p["concrete_maint_rate"], life=p["concrete_life"]),
        ]
    if s == "joints":
        return [
            dict(key="fishplate", ic=q["fishplates"] * p["fishplate_cost"], m=p["fishplate_maint_rate"], life=p["fishplate_life"]),
            dict(key="weld", ic=q["welds"] * p["weld_joint_cost"], m=p["weld_maint_rate"], life=p["weld_life"]),
        ]
    return [
        dict(key="ballast", ic=q["ballast_m3"] * FT3_PER_M3 * p["ballast_cost_per_cft"], m=p["ballasted_maint_rate"], life=p["ballast_life"]),
        dict(key="slab", ic=q["slab_length_m"] * p["slab_ic_per_m"], m=p["slab_maint_rate"], life=p["slab_life"]),
    ]


def run_lcca(form: Dict, include_end: bool = False) -> Dict:
    p = build_params(form)
    q = quantities(p)
    opts = _options(p, q)
    horizons = p["analysis_years"]
    results, cash = [], {"labels": list(range(0, max(horizons) + 1))}
    for tag, o in zip(("a", "b"), opts):
        mult = maintenance_multiplier(o["key"], p["model_mode"], p["env_factor"])
        annual = o["m"] * mult * o["ic"]
        res = analyse_option(o["ic"], annual, o["life"], p["replacement_rate"], p["discount_rate"], horizons, include_end)
        results.append(res)
        top = max(horizons)
        ys = {int(round(t)) for t in replacement_years(o["life"], top, include_end)}   # chart year index
        cash[tag] = {
            "maint": [0] + [annual] * top,
            "repl": [o["ic"]] + [p["replacement_rate"] * o["ic"] if t in ys else 0 for t in range(1, top + 1)],
        }
    name_a, name_b = SCENARIOS[p["scenario_id"]]
    p["quantities"] = q
    return {
        "params": p,
        "opt_a_name": name_a,
        "opt_b_name": name_b,
        "results_a": results[0],
        "results_b": results[1],
        "cash_flow": cash,
        "version": VERSION,
    }


if __name__ == "__main__":
    out = run_lcca({})
    print(f"LCCA engine v{VERSION}  scenario={out['params']['scenario_id']}  r={out['params']['discount_rate']:.4f}")
    for n in out["params"]["analysis_years"]:
        a, b = out["results_a"][n], out["results_b"][n]
        print(f"{n:>3} y   {out['opt_a_name']}: {a['lcc']:>16,.0f}   {out['opt_b_name']}: {b['lcc']:>16,.0f}")
