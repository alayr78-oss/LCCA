"""Verification tests for lcca_model.py.

Run:  python tests/test_lcca_model.py      (or: python -m pytest tests)

live_baseline.json holds outputs captured from the deployed tool (version before this release).
The financial core is checked against it; quantity logic, input checks and the sensitivity rule
were changed on purpose and are checked against hand calculations instead.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lcca_model as m  # noqa: E402

HERE = os.path.dirname(__file__)
LIVE_LIVES = {  # service lives the deployed tool used (version before this release)
    "sleepers": (25, 50), "joints": (10, 50), "track_system": (12.5, 100),
}


def _raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except m.InputError:
        return True
    return False


def test_core_matches_deployed_tool():
    cases = json.load(open(os.path.join(HERE, "live_baseline.json")))
    worst = 0.0
    for c in cases:
        r = 0.08
        if c["label"] == "r=5%":
            r = 0.05
        if c["label"] == "sens+0.1":
            r = 0.18  # the deployed tool added 0.10 to the rate
        years = [int(x.rstrip("y")) for x in c["labels"]]
        lives = LIVE_LIVES[c["scenario"]]
        for tag, life in zip(("a", "b"), lives):
            res = m.analyse_option(c[f"ic_{tag}"], c[f"maint_{tag}"], life, 0.40, r, years, include_end=True)
            for i, n in enumerate(years):
                worst = max(worst, abs(res[n]["lcc"] - c[f"lcc_{tag}"][i]), abs(res[n]["eac"] - c[f"eac_{tag}"][i]))
    assert worst < 0.01, worst
    return worst


def test_independent_year_by_year_sum():
    r, ic, a, life, rho = 0.08, 100e6, 5e6, 10, 0.4
    for n in (10, 25, 50):
        pv = ic + sum(a / (1 + r) ** t for t in range(1, n + 1))
        pv += sum(rho * ic / (1 + r) ** t for t in range(life, n, life))      # end of horizon excluded
        got = m.analyse_option(ic, a, life, rho, r, [n])[n]["lcc"]
        assert abs(got - pv) < 1e-6


def test_lcc_never_falls_with_horizon():
    for sid in m.SCENARIOS:
        for strict in (False, True):
            for years in ("1, 5, 10, 15, 20, 25", "25, 30, 40, 50, 75, 100"):
                out = m.run_lcca({"scenario_id": sid, "target_years": years}, include_end=strict)
                for key in ("results_a", "results_b"):
                    v = [out[key][n]["lcc"] for n in out["params"]["analysis_years"]]
                    assert all(x <= y + 1e-6 for x, y in zip(v, v[1:])), (sid, key, years)


def test_zero_discount_rate():
    out = m.run_lcca({"discount_rate": "0", "target_years": "10, 50"})
    for key in ("results_a", "results_b"):
        for n in (10, 50):
            r = out[key][n]
            expected = r["initial_cost"] + r["annual_maintenance"] * n + 0.4 * r["initial_cost"] * r["num_replacements"]
            assert abs(r["lcc"] - expected) < 1e-6
            assert abs(r["eac"] - r["lcc"] / n) < 1e-6


def test_quantities_by_hand():
    q = m.quantities(m.build_params({}))
    assert q["panels_per_track"] == 3520                      # 44,000 m / 12.5 m
    assert q["wooden_per_rail"] == 15                         # floor(12.5 + 2 + 0.5)
    assert q["wooden_count"] == 3520 * 15 * 2 == 105_600
    assert q["concrete_count"] == 3520 * 14 * 2 == 98_560
    assert q["joints"] == 3519 * 2 * 2 == 14_076
    assert q["fishplates"] == 28_152
    assert q["welds"] == 160 * 44 * 2 == 14_080
    assert abs(q["ballast_m3"] - 2.676 * 0.25 * 44_000 * 2) < 1e-6
    assert q["slab_length_m"] == 88_000


def test_default_sleeper_case_by_hand():
    out = m.run_lcca({})
    ic_w, ic_c = 105_600 * 600, 98_560 * 960
    r, rho = 0.08, 0.4
    ann = lambda n: (1 - (1 + r) ** -n) / r
    w50 = ic_w * (1 + 0.08 * ann(50)) + sum(rho * ic_w / (1 + r) ** t for t in (10, 20, 30, 40))
    c50 = ic_c * (1 + 0.03 * ann(50)) + rho * ic_c / (1 + r) ** 35
    assert abs(out["results_a"][50]["lcc"] - w50) < 1e-4
    assert abs(out["results_b"][50]["lcc"] - c50) < 1e-4
    assert abs(out["results_b"][50]["eac"] - c50 * m.capital_recovery_factor(r, 50)) < 1e-4


def test_replacement_years_and_end_of_horizon_rule():
    assert m.replacement_years(12.5, 50, include_end=True) == [12.5, 25.0, 37.5, 50.0]
    assert m.replacement_years(12.5, 50, include_end=False) == [12.5, 25.0, 37.5]
    assert m.replacement_years(10, 10) == [] and m.replacement_years(10, 10, True) == [10]
    assert m.replacement_years(35, 50) == [35]


def test_sensitivity_is_relative():
    assert abs(m.build_params({"sensitivity": "0.1"})["discount_rate"] - 0.088) < 1e-12
    assert abs(m.build_params({"sensitivity": "-0.1"})["discount_rate"] - 0.072) < 1e-12


def test_maintenance_multipliers():
    f = m.maintenance_multiplier
    assert f("wooden", "proactive", 2.0) == 2.0 and f("concrete", "proactive", 2.0) == 1.1
    assert abs(f("wooden", "reactive", 1.5) - 1.8) < 1e-12 and abs(f("slab", "reactive", 1.0) - 1.2) < 1e-12
    assert f("fishplate", "proactive", 1.5) == 1.1 and f("ballast", "proactive", 1.0) == 1.0


def test_input_validation():
    bad = [{"track_length_km": "0"}, {"track_length_km": "-5"}, {"discount_rate": "abc"}, {"discount_rate": "-2"},
           {"wooden_sleeper_cost": "-600"}, {"wooden_maint_rate": "500"}, {"target_years": "abc"}, {"target_years": "0"},
           {"target_years": "5, 500"}, {"number_of_tracks": "0"}, {"number_of_tracks": "1.5"}, {"scenario_id": "x"},
           {"wooden_life": "0"}, {"env_factor": "9"}, {"sensitivity": "2"}]
    for f in bad:
        assert _raises(m.build_params, f), f
    assert m.build_params({"track_length_km": "", "discount_rate": ""})["discount_rate"] == 0.08  # empty -> default
    assert m.build_params({"target_years": "50, 25 10"})["analysis_years"] == [10, 25, 50]


def test_scaling_with_tracks_and_length():
    one = m.run_lcca({"number_of_tracks": "1"})["results_a"][50]["initial_cost"]
    two = m.run_lcca({"number_of_tracks": "2"})["results_a"][50]["initial_cost"]
    assert abs(two - 2 * one) < 1e-6


if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            res = fn()
            print(f"PASS  {name}" + (f"   (largest difference to deployed tool: Rs {res:.4f})" if res is not None else ""))
            n += 1
    print(f"{n} tests passed")
