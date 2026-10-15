# Correction log

Each entry gives what was previously stated, why it was wrong or unsupported, and what replaced it.
Entries apply to every deliverable: this repository and app, the live project report, the case study
(web page and PDF) and any slides derived from them.

## C1. Wrong dataset used for the "original data audit" (October 2026)
- **Previously stated.** "The original project's response file failed data-quality checks (Bartlett p = 0.47,
  KMO = 0.46, Cronbach's α for trust = 0.21); it contained 27 under-18 and 36 non-user respondents; the deck's
  statistics could not be reproduced." This was used to justify replacing the survey with synthetic data.
- **What was wrong.** The audited file (222 responses) came from a **different project's survey**. It was attached
  to this project in error. None of those statements describe Team Anova's data.
- **Correction.** The 222-response file is excluded entirely: not merged, not compared, not cited, and not stored in
  this repository. Team Anova's genuine file (112 responses, collected 13–17 January 2026) was audited independently
  and analysed under a pre-specified plan ([ANALYSIS_PLAN](primary/ANALYSIS_PLAN.md)). It is factorable
  (KMO = 0.865; Bartlett p < 0.001), has no missing item responses and no minors.
- **Deck numbers.** The final presentation's statistics are reproduced closely (differences of 0.009 or less) from all 112 responses
  using only the four items that Google Forms exported as numbers (Q10, Q12, Q14, Q15): α(Q14, Q15) 0.764 vs
  0.755 reported; r(Q10, Q12) 0.691 vs 0.69; r(Q14, Q15) 0.618 vs 0.61; R² for Q10 + Q12 → Q15 0.215 vs 0.207;
  B for Q15 → Q14 0.603 vs 0.596 (`outputs/primary/deck_reproduction.csv`). The small differences may reflect an
  export taken before the last few responses arrived; this cannot be checked. The earlier claim that the deck could not be reproduced is withdrawn.

## C2. Synthetic results presented as key results
- **Previously stated.** README, case study and report gave "key results" from the synthetic demo (n = 206,
  R² = 0.44, governance β = 0.31, trust → usage β = 0.46, "trust fully mediates every driver", Kano categories).
- **What was wrong.** Those numbers describe a simulation whose answers were fixed by the generating model.
  They are not evidence about anyone.
- **Correction.** Every synthetic output is labelled "method illustration, not findings" (app banner,
  `RESULTS_SYNTHETIC.md` header, data card). Findings now come only from the primary survey.

## C3. The deck's analysis of the genuine data
These are limits of the original analysis, recorded so that the reanalysis can be understood.
- Only the four numerically exported items were analysed. The six text-coded items, including all of transparency
  (H1) and consent (H2), were left out, so H1 and H2 were never tested.
- Non-users (37) and one blank were included, although the items ask about "the platform".
- Q15 ("my level of trust strongly influences my decision…") was treated as a measure of trust. It measures how
  important trust is to the respondent.
- **Correction.** All ten items are coded; the analytic sample is the 74 users; Q14 is treated as a single-item
  trust-based continuance intention (TBCI) proxy; Q15 is reported separately.

## C4. Hypothesis H5 and mediation
- **Previously stated.** Trust → continued usage was supported, and trust fully mediated the drivers' effects
  (synthetic data); the deck reported Q15 → Q14 as the trust → usage link.
- **What was wrong.** The form has no separate measure of trust and of usage intention. Q14 contains both.
- **Correction.** H5 and mediation are reported as **not testable** with this instrument. The Q14–Q15 correlation
  (Spearman ρ = 0.49) is descriptive only.

## C5. Causal and strength language
- **Previously stated.** Drivers "increase", "explain" or "drive" trust.
- **Correction.** The survey is cross-sectional and self-reported. Results are reported as associations with the
  TBCI proxy. Governance & accountability is the only construct with a robust *unique* association; transparency,
  consent and communication are associated with TBCI on their own but not after the other constructs are held
  constant. Because one factor dominates the ten items (54% of variance), the four constructs are not empirically
  separable in this data.

## C6. Survey instrument "v2"
- **Previously stated.** "Questionnaire v2" corrected the Team Anova form.
- **What was wrong.** It was derived from the other project's form.
- **Correction.** Renamed [Synthetic demo instrument](SYNTHETIC_DEMO_INSTRUMENT.md) and kept only for the simulation.
  A new [follow-up instrument](primary/FOLLOW_UP_RESEARCH.md#4-follow-up-instrument) keeps the project's ten items
  and adds direct trust items, a separate continuance-intention scale, a third item per construct, screening,
  context questions (location, language, kiosk use, health-literacy screener) and an attention check.

## C7. Kano analysis
- **Previously stated.** Feature categories (Must-be, Performance, Attractive) and an MVP roadmap from the Kano page.
- **What was wrong.** No Kano survey was run; the 110 responses are simulated.
- **Correction.** Kano output is labelled illustrative. Feature priority rests on the survey's lowest-agreement items
  (Q10, Q11, Q7) and on team judgement (RICE), both labelled as such.

## C8. Audit-ledger guarantees
- **Previously stated.** The hash-chained ledger is "tamper-evident".
- **What was incomplete.** Without an external anchor the chain cannot detect deletion of the newest entries or a
  full recomputation after an edit; no ledger can show that an unlogged access happened.
- **Correction.** Added `Locker.anchor()` and anchor-aware `verify_chain()`, demo buttons for deletion and
  recomputation, tests for each case, and a "guarantees and limits" note in the DPO console.

## C9. Regulatory wording
- Grievance period: changed to "grievances answered within the period the fiduciary publishes, which may not exceed
  90 days (Rule 14(3))", instead of a 90-day limit for every rights request.
- Timeline: dates given as notified (Rules published 13/14 Nov 2025; consent-manager provisions from 13 Nov 2026;
  substantive duties from 13 May 2027), with a note that a 2026 MeitY proposal to shorten the transition had not been
  notified in the sources reviewed (October 2026).
- The DPDP page states that it is an educational self-assessment, not legal advice or certification.

## C10. Business case
- **Correction.** The ROI page and report now classify every input as an assumption, and every output (NPV, payback,
  Monte Carlo share of runs with NPV > 0) as a simulation on those assumptions. No ZiffyHealth operating data was
  available. "Probability NPV > 0" is renamed "share of simulated runs with NPV > 0".

## C11. Earlier numerical corrections (before October 2026)
- Decision-matrix robustness: "holds in 60% of weight draws" corrected to 75–80%.
- Case study break-even repeat-visit uplift: "about 20%" corrected to 28%.
