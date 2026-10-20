# app.py
# Flask application for the Railway LCCA Calculator (Karachi Circular Railway)
import json

from flask import Flask, render_template, request

from lcca_model import DEFAULTS, InputError, run_lcca

app = Flask(__name__)


def pk_money(value):
    """Format rupee amounts in Lakh / Crore notation."""
    try:
        if value is None:
            return "0"
        val = float(value)
        if val == 0:
            return "0"
        sign = "-" if val < 0 else ""
        val = abs(val)
        if val >= 10000000:
            return f"{sign}{val / 10000000:.2f} Crore"
        if val >= 100000:
            return f"{sign}{val / 100000:.2f} Lakh"
        return f"{sign}{val:,.2f}"
    except (TypeError, ValueError):
        return value


app.jinja_env.filters["pk_money"] = pk_money


@app.route("/", methods=["GET"])
def landing():
    return render_template("landing.html")


@app.route("/configure", methods=["GET"])
def index():
    return render_template("index.html", defaults=DEFAULTS)


@app.route("/results", methods=["POST"])
def results():
    try:
        analysis = run_lcca(request.form.to_dict())
    except InputError as exc:
        return render_template("index.html", defaults=DEFAULTS, errors=exc.errors), 400

    params = analysis["params"]
    chart_lcc = {"labels": [], "a": [], "b": [], "eac_a": [], "eac_b": []}
    table_rows = []
    for yr in params["analysis_years"]:
        ra, rb = analysis["results_a"][yr], analysis["results_b"][yr]
        chart_lcc["labels"].append(f"{yr}y")
        chart_lcc["a"].append(ra["lcc"])
        chart_lcc["b"].append(rb["lcc"])
        chart_lcc["eac_a"].append(ra["eac"])
        chart_lcc["eac_b"].append(rb["eac"])
        table_rows.append({
            "years": yr,
            "a_ic": ra["initial_cost"], "a_npv": ra["npv_maintenance"], "a_repl": ra["npv_replacement"],
            "a_lcc": ra["lcc"], "a_eac": ra["eac"],
            "b_ic": rb["initial_cost"], "b_npv": rb["npv_maintenance"], "b_repl": rb["npv_replacement"],
            "b_lcc": rb["lcc"], "b_eac": rb["eac"],
        })

    return render_template(
        "results.html",
        analysis=analysis,
        params=params,
        table_rows=table_rows,
        chart_lcc=json.dumps(chart_lcc),
        cash_flow=json.dumps(analysis["cash_flow"]),
    )


if __name__ == "__main__":
    app.run(debug=False)
