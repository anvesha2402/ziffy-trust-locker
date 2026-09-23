# Data card: `synthetic_survey_v2_SYNTHETIC`

| | |
|---|---|
| **Type** | Synthetic (simulated). **No real respondents.** |
| **Generator** | `core/sample_data.py::synthetic_survey(n_raw=262, seed=2026)` |
| **Format** | Google Forms export: `Timestamp`, screening questions, then `Section [statement]` Likert columns with text answers |
| **Rows** | 262 raw → 206 after documented exclusions |
| **Purpose** | Demonstrate and test the analysis pipeline and app; teach the corrected instrument design |
| **Not for** | Any claim about Indian patients, ZiffyHealth users or digital-health adoption |

## Why synthetic
The original project's response file failed data-quality checks: inter-item correlations were indistinguishable from randomly shuffled answers (Bartlett p = 0.47, KMO = 0.46, Cronbach's α for trust = 0.21). It also contained 27 under-18 and 36 non-user respondents. Since that data can't support inferences, and the original dataset couldn't be located, the pipeline is shown on a transparent simulation instead.

## Instrument v2: what changed from the original form
| Issue in v1 | Fix in v2 |
|---|---|
| H3 (Governance) and H4 (Communication) had no measurement items | 3 items each |
| Transparency had 1 item; consent had 2, mixed into a privacy section | Separate 3-item scales |
| Pricing-clarity item inside "Data Privacy & Transparency" | Moved to its own section |
| "Trust increased with experience" and "if concerns are addressed" mixed into Usage Intention | Excluded from the USE scale; the conditional item is kept as a separate outcome |
| No consent, age or user screening | Consent → 18+ → past-year-user branching |
| "None of the above" could be ticked alongside services | Exclusive option |
| No attention check | Instructed-response item added |

## Generating model (standardised latent variables)
```
TRU = .20 TRN + .17 CON + .18 GOV + .14 COM + .18 PRV + .07 CRD + .11 REL − .10 BDM + ε
USE = .52 TRU + .10 REL − .12 BUS + ε
Rural/semi-urban: lower TRN, higher BUS · Age 55+: higher BUS
Item loadings 0.62–0.86 · Careless responders: 4.5 % random clickers, 3 % straight-liners
Arrival times: five share waves with exponential decay (organic, bursty)
```
Because the true model is known, the app can be checked for **recovery**. Note that the regression finds CON and COM non-significant even though their true effects are non-zero. This is a realistic power and collinearity lesson: at n ≈ 200, small effects that overlap with correlated drivers are hard to separate.
