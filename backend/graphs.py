# graphs.py
# Chart generation for Railway LCCA using Matplotlib
# All figures saved to static/ for embedding in Flask templates

import os
import matplotlib
matplotlib.use("Agg")           # non-interactive backend (safe for Flask)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import List, Dict

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Consistent colour palette
CLR_WOOD  = "#8B5E3C"
CLR_CONC  = "#4472C4"
CLR_MAINT = "#ED7D31"
CLR_REPL  = "#A9D18E"
CLR_IC    = "#5B9BD5"
BG        = "#FAFAFA"


def _save(fig: plt.Figure, filename: str) -> str:
    """Save figure to static/ and return relative path. Cleans up old cached images."""
    import uuid
    import glob
    
    base = filename.split('.')[0]
    
    # Clean up old images for this chart type
    for old_file in glob.glob(os.path.join(STATIC_DIR, f"{base}_*.png")):
        try:
            os.remove(old_file)
        except OSError:
            pass
            
    # Also clean up the exact old base filename if it exists
    try:
        exact_old = os.path.join(STATIC_DIR, filename)
        if os.path.exists(exact_old):
            os.remove(exact_old)
    except OSError:
        pass
        
    unique_filename = f"{base}_{uuid.uuid4().hex[:8]}.png"
    path = os.path.join(STATIC_DIR, unique_filename)
    fig.savefig(path, dpi=120, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return unique_filename


# ─── 1. LCC vs Time ────────────────────────────────────────────────────────────

def plot_lcc_vs_time(years: List[int],
                     wood_lcc: List[float],
                     conc_lcc: List[float],
                     output_file: str = "lcc_vs_time.png") -> str:
    """
    Grouped bar chart: LCC (Rs) at each analysis horizon for
    wooden vs concrete sleepers.
    """
    x = np.arange(len(years))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG)
    bars_w = ax.bar(x - width / 2, [v / 1e6 for v in wood_lcc],
                    width, label="Wooden", color=CLR_WOOD)
    bars_c = ax.bar(x + width / 2, [v / 1e6 for v in conc_lcc],
                    width, label="Concrete", color=CLR_CONC)

    ax.set_xlabel("Analysis Period (years)", fontsize=11)
    ax.set_ylabel("Life Cycle Cost (Rs Million)", fontsize=11)
    ax.set_title("LCC Comparison: Wooden vs Concrete Sleepers", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{y} yrs" for y in years])
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}M"))
    ax.set_facecolor(BG)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Value labels on bars
    for bar in list(bars_w) + list(bars_c):
        h = bar.get_height()
        ax.annotate(f"{h:.1f}M",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    return _save(fig, output_file)


# ─── 2. Cumulative Cost Over Time (line chart) ─────────────────────────────────

def plot_cumulative_cost(wood_results: Dict, conc_results: Dict,
                         r: float, max_years: int = 50,
                         output_file: str = "cumulative_cost.png") -> str:
    """
    Line chart showing how total LCC accumulates year-by-year.
    """
    from lcca_model import npv_annuity, _replacement_npv

    year_range = list(range(0, max_years + 1))
    wood_ic  = wood_results[max(wood_results)]["initial_cost"]
    conc_ic  = conc_results[max(conc_results)]["initial_cost"]
    wood_maint_ann = wood_results[max(wood_results)]["annual_maintenance"]
    conc_maint_ann = conc_results[max(conc_results)]["annual_maintenance"]

    wood_vals, conc_vals = [], []
    for t in year_range:
        if t == 0:
            wood_vals.append(wood_ic / 1e6)
            conc_vals.append(conc_ic / 1e6)
        else:
            w_npv = npv_annuity(wood_maint_ann, r, t)
            w_repl = _replacement_npv(wood_ic, 0.40, 25, t, r)
            wood_vals.append((wood_ic + w_npv + w_repl) / 1e6)

            c_npv = npv_annuity(conc_maint_ann, r, t)
            conc_vals.append((conc_ic + c_npv) / 1e6)

    fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG)
    ax.plot(year_range, wood_vals, color=CLR_WOOD, linewidth=2.5, label="Wooden")
    ax.plot(year_range, conc_vals, color=CLR_CONC, linewidth=2.5, label="Concrete")
    ax.fill_between(year_range, wood_vals, conc_vals,
                    where=[w > c for w, c in zip(wood_vals, conc_vals)],
                    alpha=0.12, color=CLR_WOOD, label="Wood > Conc")
    ax.fill_between(year_range, wood_vals, conc_vals,
                    where=[c >= w for w, c in zip(wood_vals, conc_vals)],
                    alpha=0.12, color=CLR_CONC, label="Conc ≥ Wood")

    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Cumulative LCC (Rs Million)", fontsize=11)
    ax.set_title("Cumulative Life Cycle Cost Over Time", fontsize=13, fontweight="bold")
    ax.legend()
    ax.set_facecolor(BG)
    ax.grid(linestyle="--", alpha=0.35)
    fig.tight_layout()
    return _save(fig, output_file)


# ─── 3. Cost Component Pie ─────────────────────────────────────────────────────

def plot_pie_cost_breakdown(wood_results: Dict, conc_results: Dict,
                             horizon: int = 50,
                             output_file: str = "pie_breakdown.png") -> str:
    """
    Side-by-side pie charts: IC vs Maintenance vs Replacement.
    """
    wr = wood_results[horizon]
    cr = conc_results[horizon]

    def slices(r):
        ic    = r["initial_cost"]
        maint = r["npv_maintenance"]
        repl  = r.get("npv_replacement", 0)
        return [ic, maint, repl] if repl else [ic, maint]

    labels_w = ["Initial Cost", "Maintenance NPV", "Replacement NPV"]
    labels_c = ["Initial Cost", "Maintenance NPV"]
    colours  = [CLR_IC, CLR_MAINT, CLR_REPL]

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), facecolor=BG)
    for ax, res, title, has_repl in [
        (axes[0], wr, f"Wooden — {horizon} yrs", True),
        (axes[1], cr, f"Concrete — {horizon} yrs", False),
    ]:
        vals   = slices(res)
        lbls   = labels_w if has_repl else labels_c
        clrs   = colours[:len(vals)]
        wedges, texts, autotexts = ax.pie(
            vals, labels=None, autopct="%1.1f%%",
            colors=clrs, startangle=140,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5})
        for at in autotexts:
            at.set_fontsize(9)
        ax.set_title(title, fontsize=11, fontweight="bold", pad=12)
        ax.legend(wedges, [f"{l}\n(Rs {v/1e6:.1f}M)" for l, v in zip(lbls, vals)],
                  loc="lower center", bbox_to_anchor=(0.5, -0.22),
                  fontsize=7.5, frameon=False, ncol=1)

    fig.suptitle("Cost Component Breakdown", fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    return _save(fig, output_file)


# ─── 4. Maintenance Timeline (cash flows) ──────────────────────────────────────

def plot_maintenance_timeline(wood_annual: float, conc_annual: float,
                               max_years: int = 50,
                               output_file: str = "maintenance_timeline.png") -> str:
    """
    Bar chart of undiscounted annual maintenance cash flows,
    plus vertical lines at wooden replacement years.
    """
    years = list(range(1, max_years + 1))
    w_vals = [wood_annual / 1e6] * max_years
    c_vals = [conc_annual / 1e6] * max_years

    fig, ax = plt.subplots(figsize=(11, 5), facecolor=BG)
    x = np.arange(1, max_years + 1)
    ax.bar(x - 0.2, w_vals, 0.4, color=CLR_WOOD, alpha=0.85, label="Wooden maint.")
    ax.bar(x + 0.2, c_vals, 0.4, color=CLR_CONC, alpha=0.85, label="Concrete maint.")

    # Mark replacement years for wooden sleepers
    for yr in [25, 50]:
        if yr <= max_years:
            ax.axvline(yr, color=CLR_REPL, linewidth=2, linestyle="--",
                       label="Wood replacement" if yr == 25 else "")
            ax.annotate(f"Replace\n(Yr {yr})",
                        xy=(yr, max(w_vals) * 0.9), ha="center",
                        fontsize=8, color="#2E7D32")

    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Annual Maintenance Cost (Rs Million)", fontsize=11)
    ax.set_title("Annual Maintenance Cash Flows", fontsize=13, fontweight="bold")
    ax.set_xlim(0, max_years + 1)
    ax.legend()
    ax.set_facecolor(BG)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    return _save(fig, output_file)


# ─── 5. EAC Comparison ─────────────────────────────────────────────────────────

def plot_eac_comparison(years: List[int],
                        wood_eac: List[float],
                        conc_eac: List[float],
                        output_file: str = "eac_comparison.png") -> str:
    """
    Grouped bar chart of Equivalent Annual Cost for each horizon.
    """
    x = np.arange(len(years))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG)
    ax.bar(x - width / 2, [v / 1e6 for v in wood_eac], width, label="Wooden", color=CLR_WOOD)
    ax.bar(x + width / 2, [v / 1e6 for v in conc_eac], width, label="Concrete", color=CLR_CONC)

    ax.set_xlabel("Analysis Period (years)", fontsize=11)
    ax.set_ylabel("EAC (Rs Million / year)", fontsize=11)
    ax.set_title("Equivalent Annual Cost Comparison", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{y} yrs" for y in years])
    ax.legend()
    ax.set_facecolor(BG)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    return _save(fig, output_file)


# ─── Generate all charts ───────────────────────────────────────────────────────

def generate_all_charts(wood_results: Dict, conc_results: Dict,
                         params: Dict) -> Dict[str, str]:
    """
    Convenience function: generate and save all charts.
    Returns a dict mapping chart name → filename in static/.
    """
    years = params["analysis_years"]
    r     = params["discount_rate"]

    wood_lcc  = [wood_results[y]["lcc"]  for y in years]
    conc_lcc  = [conc_results[y]["lcc"]  for y in years]
    wood_eac  = [wood_results[y]["eac"]  for y in years]
    conc_eac  = [conc_results[y]["eac"]  for y in years]

    wood_ann  = wood_results[years[0]]["annual_maintenance"]
    conc_ann  = conc_results[years[0]]["annual_maintenance"]

    charts = {}
    charts["lcc_vs_time"]         = plot_lcc_vs_time(years, wood_lcc, conc_lcc)
    charts["cumulative_cost"]     = plot_cumulative_cost(wood_results, conc_results, r)
    charts["pie_breakdown"]       = plot_pie_cost_breakdown(wood_results, conc_results)
    charts["maintenance_timeline"]= plot_maintenance_timeline(wood_ann, conc_ann)
    charts["eac_comparison"]      = plot_eac_comparison(years, wood_eac, conc_eac)
    return charts
