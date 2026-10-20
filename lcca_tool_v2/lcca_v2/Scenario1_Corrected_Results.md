# Scenario 1 results from the corrected tool (wooden vs concrete sleepers)

Settings: 44 km, 2 tracks, 12.5 m rail panels, discount rate 8 %, replacement 40 % of initial cost, maintenance 8 % (timber) and 3 % (PSC), service life 10 years (timber) and 35 years (PSC). Quantities: 105,600 timber and 98,560 PSC sleepers. Amounts in rupees.

## Base case

| Horizon | Timber IC | Timber maint. PV | Timber repl. PV | Timber LCC | Timber EAC | PSC IC | PSC maint. PV | PSC repl. PV | PSC LCC | PSC EAC |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 years | 63,360,000 | 34,012,061 | 0 | **97,372,061** | 14,511,308 | 94,617,600 | 19,046,754 | 0 | **113,664,354** | 16,939,341 |
| 25 years | 63,360,000 | 54,108,306 | 17,176,686 | **134,644,991** | 12,613,378 | 94,617,600 | 30,300,651 | 0 | **124,918,251** | 11,702,189 |
| 50 years | 63,360,000 | 62,009,087 | 20,861,913 | **146,231,000** | 11,953,340 | 94,617,600 | 34,725,089 | 2,559,767 | **131,902,456** | 10,782,084 |

Timber is cheaper over 10 years. Concrete becomes cheaper from year 16 and the gap grows to Rs 14.3 M (9.8 % of the timber cost) at 50 years.

## Sensitivity (LCC in Rs million, timber / PSC)

| Case | 25 years | 50 years | Cheaper at 50 years |
|---|---|---|---|
| Base | 134.6 / 124.9 | 146.2 / 131.9 | PSC |
| Timber life 8 years | 142.6 / 124.9 | 154.4 / 131.9 | PSC |
| Timber life 12 years | 131.5 / 124.9 | 141.6 / 131.9 | PSC |
| PSC life 30 years | 134.6 / 124.9 | 146.2 / 133.1 | PSC |
| PSC life 40 years | 134.6 / 124.9 | 146.2 / 131.1 | PSC |
| Timber 12 and PSC 30 years (least favourable to PSC) | 131.5 / 124.9 | 141.6 / 133.1 | PSC |
| Replacement 70 % | 147.5 / 124.9 | 161.9 / 133.8 | PSC |
| Replacement 100 % | 160.4 / 124.9 | 177.5 / 135.7 | PSC |
| Discount rate 6 % | 150.2 / 130.9 | 172.2 / 144.3 | PSC |
| Discount rate 10 % | 122.9 / 120.4 | 129.2 / 124.1 | PSC |
| Reactive maintenance (x 1.2) | 145.5 / 131.0 | 158.6 / 138.8 | PSC |
| Coastal factor 1.5 | 161.7 / 127.9 | 177.2 / 135.4 | PSC |
| Severe factor 2.0 | 188.8 / 127.9 | 208.2 / 135.4 | PSC |
| **Uniform 3 % maintenance (Table 5)** | 100.8 / 124.9 | 107.5 / 131.9 | **Timber** |

The ranking flips only when the timber maintenance rate is close to the PSC rate. With PSC at 3 %, concrete is cheaper at 50 years whenever timber maintenance is above about 6.2 % (6.6 % at 25 years). The result therefore rests on the 8 % timber maintenance rate, which needs a source in the paper.

## Conventions
- A replacement exactly at the end of the horizon is not charged. If it is charged, the 10-year timber LCC rises to Rs 109.1 M and the 50-year timber LCC to Rs 146.8 M. The concrete values and the ranking at 25 and 50 years do not change.
- The deployed tool's old defaults (3.81 m panels, one track, timber life 25 years, PSC life 50 years) gave Rs 159.7 / 198.8 / 212.6 M for timber and Rs 186.5 / 204.9 / 213.5 M for PSC.
