# Railway LCCA Calculator (Karachi Circular Railway)

Flask web tool that compares the life cycle cost (LCC) and equivalent annual cost (EAC) of two track options.

| Scenario | Option A | Option B |
|---|---|---|
| 1 | Hardwood timber sleepers | Pre-stressed concrete sleepers |
| 2 | Fishplate jointed track | Thermit welded track |
| 3 | Ballast bed | Slab track |

## Model

For each option and analysis period n (r = discount rate, IC = initial cost, m = maintenance rate, rho = replacement rate):

```
PV_maintenance = m * IC * (1 - (1 + r)^-n) / r
PV_replacement = sum over replacement times t of  rho * IC / (1 + r)^t      (t = life, 2 x life, ...  < n)
LCC            = IC + PV_maintenance + PV_replacement
EAC            = LCC * r (1 + r)^n / ((1 + r)^n - 1)
```

- A replacement that falls exactly at the end of the analysis period is not charged.
- Maintenance strategy "reactive" multiplies maintenance by 1.2. The environmental factor multiplies maintenance of timber and ballast by the full factor and of all other options by 1.1 when the factor is above 1.
- The sensitivity setting multiplies the discount rate by (1 + s), so +10 % turns 8 % into 8.8 %.
- Costs are in rupees at constant prices. No user, environmental or residual value is included.

## Defaults

Route 44 km, 2 tracks, rail panel 12.5 m, discount rate 8 %, replacement 40 % of initial cost, periods 10, 25, 50 years.
Maintenance rates: timber 8 %, PSC 3 %, fishplate 8 %, weld 3 %, ballast 5 %, slab 1.5 %.
Service lives (years): timber 10, PSC 35, fishplate 10, weld 50, ballast 12.5, slab 100.

## Run locally

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask --app app run               # open http://127.0.0.1:5000
```

## Verify

```bash
python tests/test_lcca_model.py
```

`tests/live_baseline.json` holds outputs of the previously deployed version. The financial core reproduces all of them to within Rs 0.01.

## Deploy on Render

Build command `pip install -r requirements.txt`, start command `gunicorn app:app`.

## Changes from the previously deployed version

1. One rail panel length (12.5 m) for all quantities. The old sleeper scenario counted rails with 3.81 m panels, which made quantities about 3.3 times too high.
2. New inputs: number of tracks, rail panel length, replacement rate and a service life for every component. Joint spacing is no longer a separate input.
3. Sensitivity is relative (rate x 1.10 or x 0.90) instead of adding or subtracting 0.10.
4. Discount rate 0 is handled. All inputs are validated and errors are shown on the form instead of a server error.
5. Service lives for timber and PSC sleepers follow Table 4 of the paper (mid-points of the ranges).
6. Ballast price default is Rs 105 per ft3 (Cantonment office rate).
7. A replacement at the exact end of the analysis period is not charged.
8. Landing page text describes only what the model calculates.
