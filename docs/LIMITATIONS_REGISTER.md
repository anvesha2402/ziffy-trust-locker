# Limitations register

Status key: **Fixed** (corrected in all deliverables) · **Mitigated** (reduced, residual risk stated) ·
**Disclosed** (cannot be fixed with the data or access available; stated wherever the affected claim appears) ·
**External** (needs information, approval or fieldwork from outside the team).

## A. Data audit

| ID | Limitation | Effect on conclusions | Status | Action taken / needed |
|---|---|---|---|---|
| A1 | A 222-response file from another project was used as "the original data" | Earlier audit, cleaning and "deck not reproducible" claims were false | Fixed | File excluded everywhere; [CORRECTION_LOG](CORRECTION_LOG.md) C1 |
| A2 | Raw file contains respondent names | Privacy risk if shared | Mitigated | Raw file kept read-only outside the repo; SHA-256 registered; only de-identified copy published; `.gitignore` blocks raw exports; test checks no raw file in repo |
| A3 | Mixed export format (6 text items, 4 numeric) | Possible method effect; deck analysed only numeric items | Mitigated | All items coded 1–5 with direction check; method effect cannot be tested from the export |
| A4 | 5 straight-liners and 4 exact-duplicate patterns among users | Could inflate correlations | Mitigated | Retained (no proof of invalidity); sensitivity analyses S2/S3 give the same conclusions |
| A5 | One blank on the screening question | Negligible | Fixed | Excluded from the analytic sample; included in S1 |
| A6 | 83 of 112 responses on the first day | Consistent with one wave of sharing; no evidence of fabrication, but no way to check identity | Disclosed | Cadence reported in the data card |

## B. Sampling and persona

| ID | Limitation | Effect | Status | Action |
|---|---|---|---|---|
| B1 | Convenience/snowball sample, no frame or response rate | No population estimates; percentages describe this sample only | Disclosed | Stated with every percentage |
| B2 | Users are mostly 18–35, students/employees, male | Results may not hold for older, rural or less digitally literate patients | Disclosed | Follow-up study stratifies by location and age |
| B3 | Location, language, kiosk use, literacy not collected | The Rajesh persona (semi-urban, Hindi-first, assisted) is not evidenced by the survey | Disclosed | Persona labelled as a design assumption; follow-up instrument adds these questions |
| B4 | "The platform" not specified | Findings are about digital-health platforms generally, not ZiffyHealth | Disclosed | Wording in all deliverables changed accordingly |
| B5 | n = 74 users | Power 0.80 only for f² ≥ 0.17 (model) or 0.11 (one predictor's unique effect) | Disclosed | Null unique effects reported as inconclusive |

## C. Methodology and causality

| ID | Limitation | Effect | Status | Action |
|---|---|---|---|---|
| C1 | No separate trust measure; Q14 combines trust and intention | H1–H4 tested against a proxy; H5 and mediation untestable | Disclosed | Pre-specified as such; follow-up instrument adds 3 trust and 3 intention items |
| C2 | Q15 measures importance of trust, not trust | Deck's use of Q15 as trust withdrawn | Fixed | Reported separately |
| C3 | Two items per construct | Reliability limited (COM Spearman-Brown 0.68) | Disclosed | Spearman-Brown reported (correct index for 2 items); no items dropped |
| C4 | One dominant factor (54%); HTMT GOV–COM > 1 | Constructs not empirically distinct; unique effects fragile | Disclosed | Stated with every regression result |
| C5 | Cross-sectional, single-source self-report | Common-method bias possible; no causal claims | Disclosed | Association language only; Harman share reported |
| C6 | Q11 and Q14 both contain "trust" | May inflate the GOV–TBCI correlation | Disclosed | Follow-up instrument rewords Q11 |
| C7 | Deck dropped H1/H2 items and included non-users | Original conclusions incomplete | Fixed | Full reanalysis under a pre-specified plan |
| C8 | Synthetic results presented as findings | False evidence | Fixed | Relabelled everywhere; removed from findings |

## D. Business case

| ID | Limitation | Effect | Status | Action |
|---|---|---|---|---|
| D1 | No ZiffyHealth operating data (volumes, call costs, repeat rates, margins) | NPV and payback are scenarios, not forecasts | Disclosed | Every input labelled assumption; outputs labelled simulation |
| D2 | Repeat-visit uplift and call deflection have no empirical basis | The two value levers are unverified; deflection dominates sensitivity | Disclosed | Pilot measures both against control clinics |
| D3 | Monte Carlo ranges are assumed | "Probability NPV > 0" overstated certainty | Fixed | Renamed "share of simulated runs" with explanation |
| D4 | Build and compliance costs not quoted by vendors | Cost side uncertain | External | Obtain quotes before a go/no-go |

## E. Compliance and legal

| ID | Limitation | Effect | Status | Action |
|---|---|---|---|---|
| E1 | Team is not legal counsel | Readiness scores are not compliance findings | Disclosed | "Not legal advice, not certification" on page and in report |
| E2 | Rule 14(3) applied too broadly (90 days for every rights request) | Wording inaccurate | Fixed | Limited to grievances |
| E3 | Transition dates may change (2026 MeitY proposal) | Timeline could shorten | Disclosed | Dates given as notified (proposal reported Jan 2026, not notified as of Oct 2026) with a check-before-use note |
| E4 | Significant Data Fiduciary status of ZiffyHealth unknown | DPIA/audit duties may or may not apply | External | Depends on government notification |
| E5 | Medical-record retention law interacts with erasure | Erasure control simplified | Disclosed | Noted in control D2 |

## F. Technical architecture

| ID | Limitation | Effect | Status | Action |
|---|---|---|---|---|
| F1 | Prototype runs on simulated patient, partners and events | No evidence it works with real systems | Disclosed | Banner on Locker page; scope table on Security page |
| F2 | Ledger could not detect truncation or full recomputation | "Tamper-evident" overstated | Mitigated | External anchor added and tested; production needs WORM/third-party anchoring |
| F3 | Ledger cannot prove completeness (unlogged access) | Logs only cover calls through the policy engine | Disclosed | Stated in DPO console; gateway enforcement proposed |
| F4 | PHI checker is a keyword list | Misses paraphrases and other languages | Disclosed | Labelled; production would need a reviewed template library |
| F5 | Consent enforced in-app only | Partners could bypass in production | Disclosed | Gateway-level enforcement in the proposed architecture |
| F6 | No usability test, accessibility audit, penetration test or load test | Unknown real-world usability and security | External | Planned in follow-up research and before production |

## G. Product-market fit and prioritisation

| ID | Limitation | Effect | Status | Action |
|---|---|---|---|---|
| G1 | No Kano survey run | Must-be / delighter classification unknown | Disclosed | Kano page labelled illustrative; real Kano study planned |
| G2 | RICE scores are team estimates | Ranking is a starting point | Disclosed | Labelled as team judgement |
| G3 | Feature priority partly inferred from item-level gaps (Q10, Q11, Q7) | Items are about platforms generally, not Locker features | Disclosed | Priority stated as provisional |
| G4 | No willingness-to-pay or adoption data | Uptake of the Locker unknown | External | Pilot measures Locker views, consent completion and opt-outs |

## H. Governance and traceability

| ID | Limitation | Effect | Status | Action |
|---|---|---|---|---|
| H1 | Analysis decisions previously undocumented | Risk of selective reporting | Fixed | [ANALYSIS_PLAN](primary/ANALYSIS_PLAN.md) fixed before hypothesis tests; deviations section |
| H2 | Numbers copied by hand into deliverables | Transcription errors (two found earlier) | Mitigated | `results.json` generated by script; tests check published numbers against recomputation |
| H3 | No client sign-off on the reanalysis | Findings not endorsed by ZiffyHealth or faculty | External | Share the correction log with the faculty mentor and company contact |
| H4 | Consent text of the Google Form not available to the analyst | Unclear whether publishing even de-identified rows is permitted | External | Confirm before the repo is public; otherwise publish aggregates only |
| H5 | Earlier deliverables (report, case study, slides) circulated with the old claims | Readers may hold superseded numbers | Mitigated | All deliverables rebuilt; correction log names what changed |
