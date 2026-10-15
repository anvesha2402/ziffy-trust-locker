# Evidence register

Every substantive claim used in the app, report and case study, with the kind of evidence behind it.

**Evidence types**
- **P — Primary, measured.** Computed from the genuine survey (n = 74 users unless stated). Reproducible with `python scripts/primary_analysis.py`.
- **S — Secondary, published.** Taken from a cited external source; not independently verified beyond that source.
- **R — Regulation.** Read from the Act, Rules or Directions; interpretation is the team's, not legal advice.
- **J — Team judgement.** Qualitative assessment by the team; not validated with ZiffyHealth.
- **A — Assumption.** A planning number with no data behind it.
- **M — Simulation.** Output computed from assumptions or from synthetic data.
- **I — Implemented in prototype.** Behaviour that runs in the app and is covered by tests; not deployed in production.

## Research findings

| # | Claim | Type | Basis | Strength / caveat |
|---|---|---|---|---|
| E1 | Only 38% of users agree their platform has strong measures to protect their data (Q10); 38% agree it would take responsibility if data were misused (Q11) | P | Item descriptives | Convenience sample; "platform" unspecified |
| E2 | 47% agree their platform is transparent about who can access their data (Q7); 28% disagree | P | Item descriptives | As above |
| E3 | Transparency, consent, governance and communication are each positively associated with TBCI (ρ = 0.46, 0.49, 0.75, 0.66; Holm p < .001) | P | Pre-specified Spearman tests | Association only; Q11 and Q14 share the word "trust", which may inflate the governance correlation |
| E4 | Governance & accountability is the only construct with a robust unique association (β = 0.50, 95% CI 0.14–0.84) | P | OLS with HC3 SEs; holds in S2, S3 and ordinal logit | Constructs overlap (one dominant factor; HTMT GOV–COM > 1) |
| E5 | Transparency, consent and communication show no unique association once the others are controlled | P | OLS | Absence of evidence, not evidence of absence (power for a single unique effect: f² ≥ 0.11) |
| E6 | Trust matters to users' continuance decisions (64% agree with Q15) | P | Item descriptive | Measures stated importance, not trust level |
| E7 | Users rate all constructs higher than non-users | P | Mann-Whitney, exploratory | Non-users rated a platform they had not used; interpret cautiously |
| E8 | Trust → continued usage (H5); mediation through trust | — | **Not testable** | No separate trust or intention measure |
| E9 | Findings apply to semi-urban, Hindi-first e-clinic patients | — | **Not supported** | Location, language, kiosk use not collected; sample mostly 18–35 students and employees |
| E10 | Kano categories of Locker features | M | Simulated responses | Illustrative only; no Kano survey run |

## Context and market

| # | Claim | Type | Source |
|---|---|---|---|
| E11 | 96.4 crore ABHA IDs created; 110 crore+ health records linked | S | ABDM dashboard as reported by Digital Health News, 12 Aug 2026 |
| E12 | 82% of Indian consumers rank data protection as a top trust factor | S | PwC Voice of the Consumer 2024 (India) |
| E13 | India digital-health market USD 19.1 bn (2025) → 90 bn (2034) | S | IMARC (market-research estimate; method not public) |
| E14 | ZiffyHealth's service model (IoT kiosk with 6 vitals incl. ECG, tele-consultation, diagnostics, pharmacy, cloud EHR) | S | ziffytech.com; project brief from the company |
| E15 | Three trust breaks in the journey (before care, hand-offs, after care) | J | Team's journey mapping from the company brief and the project deck; consistent with E1–E2 but not measured as such |

## Regulation

| # | Claim | Type | Source |
|---|---|---|---|
| E16 | DPDP Rules notified 13/14 Nov 2025; consent-manager provisions from 13 Nov 2026; substantive duties from 13 May 2027 | R | Gazette notification; PIB release 17 Nov 2025 |
| E17 | A 2026 proposal to shorten the transition to 12 months had not been notified (as of Oct 2026) | S | Business Standard, 22 Jan 2026 (proposal); compliance trackers reviewed Oct 2026; check the Gazette before relying on any date |
| E18 | Breach report to the Board within 72 hours; logs kept ≥ 1 year; grievance response period ≤ 90 days | R | DPDP Rules 2025, Rules 6, 7, 14(3) |
| E19 | CERT-In: incident report within 6 hours; logs 180 days in India | R | CERT-In Directions, 28 Apr 2022 |
| E20 | Penalty up to ₹250 crore for failing to take reasonable security safeguards | R | DPDP Act 2023, Schedule |

## Solution and business case

| # | Claim | Type | Basis |
|---|---|---|---|
| E21 | Consent is checked (purpose, data type, expiry) before every partner read in the prototype | I | `core/locker.py`; tests in `tests/` |
| E22 | Edits to ledger entries are detected; deletion/recomputation is detected only with an external anchor | I | `verify_chain`, `anchor`; tests in `tests/test_core.py` |
| E23 | Care Moment templates avoid revealing health information | I | Keyword checker; misses paraphrases |
| E24 | The Locker addresses 15 of 26 readiness controls (in whole or part) | J | Mapping in `core/dpdp.py`; assumes full production build |
| E25 | Pilot economics: NPV, payback, break-even uplift, share of simulated runs with NPV > 0 | M on A | `core/roi.py` defaults; no operating data |
| E26 | Call deflection is the most sensitive driver of the business case | M | Tornado analysis on assumed ranges |
| E27 | RICE ranking of features | J | Team estimates of reach, impact, confidence, effort |
| E28 | PESTEL, Five Forces, 7S, CBBE, ESG materiality scores | J | Team judgement from public sources |
| E29 | Patient trust, repeat visits or support calls will change after launch | — | **Not yet evidenced**; requires the pilot in `docs/primary/FOLLOW_UP_RESEARCH.md` |
