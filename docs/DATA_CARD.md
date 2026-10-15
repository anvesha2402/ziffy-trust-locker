# Data cards

This repository holds three datasets. Only the first one is evidence.

| File | Status | Use |
|---|---|---|
| `data/primary/primary_survey_deidentified.csv` | **Genuine.** Team Anova's Google Form, 112 responses | The project's findings |
| `data/synthetic_survey_v2_SYNTHETIC.csv` / `.xlsx` | Simulated. No real respondents | Method illustration and tests only |
| `data/kano_responses_SYNTHETIC.csv` | Simulated. No real respondents | Kano method illustration only |

A 222-response file from a different project's survey was once associated with this project in error. It is
**not in this repository** and is not used for any purpose (see [CORRECTION_LOG](CORRECTION_LOG.md)).

---

## 1. Primary survey (genuine)

| | |
|---|---|
| **Source** | Google Form circulated by Team Anova during the live project; sheet "Form Responses 1" |
| **Raw file** | `Gcl Primary data sheet .xlsx`, 112 rows × 16 columns, SHA-256 `d681ca83…8b445230`. Kept unchanged, read-only and **outside** the repository because it contains respondent names |
| **Collected** | 13–17 January 2026 (83 of 112 responses on the first day) |
| **Recruitment** | Convenience / snowball sharing by team members. No sampling frame, no response rate |
| **Published copy** | `data/primary/primary_survey_deidentified.csv`, created by `core/primary.py::deidentify` |
| **De-identification** | Name dropped; timestamp replaced by date only and a sequential ID (R001–R112, in submission order); gender, age band and profession kept as collected |
| **Columns** | `response_id, response_date, gender, age_band, profession, used_digital_health, Q6…Q15` |
| **Item coding** | 1 = Strongly disagree … 5 = Strongly agree. Q6–Q9, Q11, Q13 were exported as text; Q10, Q12, Q14, Q15 as numbers 1–5 (direction confirmed: every numeric item correlates positively with every text item) |
| **Missing data** | None in Q6–Q15. One blank on the usage-screening question |
| **Analytic sample** | 74 respondents who said they had used a digital-healthcare platform. 37 non-users and 1 blank are described, not analysed |
| **Analysis** | Pre-specified in [`docs/primary/ANALYSIS_PLAN.md`](primary/ANALYSIS_PLAN.md); results in [`docs/primary/RESULTS_PRIMARY.md`](primary/RESULTS_PRIMARY.md) |

### Item wording

| Code | Construct | Statement |
|---|---|---|
| Q6 | Transparency | I clearly understand how my health data is collected and used by the digital healthcare platform. |
| Q7 | Transparency | The platform is transparent about who can access my health data and when it is shared. |
| Q8 | Consent | The consent process allows me to clearly choose what type of health data I want to share. |
| Q9 | Consent | I feel confident using the platform because I can easily withdraw or modify my consent at any time. |
| Q10 | Governance | I believe the platform has strong measures in place to protect my health data from misuse. |
| Q11 | Governance | I trust that the platform would take responsibility and address issues if my data were misused. |
| Q12 | Communication | The platform communicates clearly and in a timely manner about matters related to my health data. |
| Q13 | Communication | The platform's communication makes me feel informed and reassured about my data and services. |
| Q14 | Outcome (TBCI) | Because I trust the platform, I intend to continue using it for my healthcare needs. |
| Q15 | Importance of trust | My level of trust strongly influences my decision to keep using a digital healthcare platform. |

### Known limits of this dataset
- **Who answered.** Users in the sample are mostly young (52 of 74 aged 18–35), students or employees, and male (48 of 74).
  Location, language, kiosk use and health literacy were **not collected**, so the e-clinic persona (semi-urban,
  Hindi-first, operator-assisted) is not represented in a way that can be checked.
- **"The platform" is unspecified.** Respondents rated whichever platform they had in mind. Results are about
  digital-health platforms in general, not ZiffyHealth.
- **Two items per construct.** Reliability is acceptable for TRN, CON and GOV (Spearman-Brown 0.72–0.82) and weak for
  COM (0.68). Constructs are not empirically distinct: one component dominates, and HTMT for GOV–COM exceeds 1.
- **No separate trust measure.** Q14 combines trust and intention; Q15 measures how much trust matters, not how much
  the respondent trusts. Trust → usage (H5) and mediation through trust cannot be tested.
- **Mixed export formats.** Four items were exported as numbers and six as text. If respondents saw a different
  answer format for those items, a method effect is possible; it cannot be tested from the export.
- **Data quality.** Among the 74 users, 5 gave the same answer to all ten items and 4 response patterns are exact
  duplicates of an earlier row. They are retained (no proof of invalidity) and tested in sensitivity analyses.
- **Re-identification risk.** Some cells are small (3 entrepreneurs, 2 homemakers, 8 respondents aged 47–59). Before
  publishing the de-identified file in a public repository, confirm that the form's consent text allows sharing of
  anonymised responses. If it does not, remove `data/primary/primary_survey_deidentified.csv` from the public repo and
  publish only the aggregate outputs in `outputs/primary/`.

---

## 2. Synthetic demo survey (simulated, method illustration only)

| | |
|---|---|
| **Type** | Synthetic. **No real respondents** |
| **Generator** | `core/sample_data.py::synthetic_survey(n_raw=262, seed=2026)` (deterministic) |
| **Instrument** | [Synthetic demo instrument](SYNTHETIC_DEMO_INSTRUMENT.md). Its wording was adapted from the other project's form, **not** Team Anova's |
| **Rows** | 262 raw → 206 after the pipeline's documented exclusions |
| **Purpose** | Show and test the generic Research Lab pipeline (screening flow, audit, reliability, regression, mediation) on data whose true model is known |
| **Not for** | Any claim about patients, ZiffyHealth users, digital-health adoption or the Team Anova survey |

Generating model (standardised latent variables):
```
TRU = .20 TRN + .17 CON + .18 GOV + .14 COM + .18 PRV + .07 CRD + .11 REL − .10 BDM + ε
USE = .52 TRU + .10 REL − .12 BUS + ε
Rural/semi-urban: lower TRN, higher BUS · Age 55+: higher BUS
Item loadings 0.62–0.86 · Careless responders: 4.5 % random clickers, 3 % straight-liners
```
Because the true model is known, the app can be checked for parameter recovery. Its output
([`RESULTS_SYNTHETIC.md`](RESULTS_SYNTHETIC.md)) describes the simulation only.

## 3. Synthetic Kano responses (simulated)
110 simulated respondents × 10 Locker features, generated by `core/sample_data.py::demo_kano`. No Kano survey was run
in the project, so the Kano categories shown in the app are illustrative.
