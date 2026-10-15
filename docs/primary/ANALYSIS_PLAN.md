# Analysis plan: primary survey (Health Data Locker, Team Anova)

Status: **fixed before any hypothesis test was run** on the recovered dataset. The only
inspection done beforehand was structural: column list, response coding, item-level
correlations (to confirm scale direction), eligibility counts and data-quality checks.
Any deviation from this plan is listed in Section 9.

## 1. Data source
- File: `Gcl Primary data sheet .xlsx`, sheet "Form Responses 1", the Google Form circulated for this
  live project. 112 rows × 16 columns.
- SHA-256 of the raw file: `d681ca838d795e3f3166579e97385f1bb3b96349626919ad6a69a9a38b445230`.
- The raw file contains respondent names. It is kept unchanged and read-only **outside** the repository.
  The repository holds only a de-identified copy (`data/primary/primary_survey_deidentified.csv`).
- A separate 222-response file from another project's survey was mistakenly associated with this
  project earlier. It is **excluded entirely**: it is not merged, not compared and not cited as evidence.

## 2. De-identification
- Drop `Name`.
- Replace `Timestamp` with the response date plus a sequential response ID (R001…R112, in timestamp
  order). Minute-level timing is used only inside the private audit, for cadence checks.
- Keep gender, age band and profession, as collected.

## 3. Coding
- Text Likert answers are mapped Strongly disagree = 1 … Strongly agree = 5, after trimming and
  lower-casing. Spelling variants ("Strongly agree" / "Strongly Agree") are treated as the same answer.
- Four items (Q10, Q12, Q14, Q15) were exported as numbers 1–5. Direction check: every one of them
  correlates positively with every text-coded item. 1 is therefore read as Strongly disagree and 5 as Strongly agree.
- All items are positively worded, so nothing is reverse-coded.

## 4. Item-to-construct mapping

| Construct (hypothesis) | Items | Notes |
|---|---|---|
| Data transparency (H1) | Q6 understand how data is collected and used; Q7 transparent about who can access data | 2 items |
| Consent mechanisms (H2) | Q8 can choose what data to share; Q9 confident to withdraw or modify consent | 2 items |
| Governance & accountability (H3) | Q10 strong measures protect data from misuse; Q11 platform would take responsibility | 2 items; Q10 is closer to *perceived security* |
| Communication (H4) | Q12 communicates clearly and in a timely way; Q13 communication makes me feel informed and reassured | 2 items |
| **Outcome: trust-based continuance intention (TBCI)** | Q14 "Because I trust the platform, I intend to continue using it" | Single item that combines trust with intention to continue |
| Perceived importance of trust | Q15 "My level of trust strongly influences my decision to keep using…" | Measures how much trust matters to the respondent, **not** their level of trust |

**Consequence.** The form has no item that measures digital trust on its own. H1–H4, which
specify digital trust as the outcome, are tested against the closest available proxy, TBCI (Q14),
and are reported as such. H5 (trust → continued usage) and any mediation through trust **cannot be tested**,
because there is no separate measure of trust and of usage intention.

## 5. Eligibility and samples
- **Primary analytic sample (A):** respondents answering "Yes" to prior use of a digital-healthcare
  platform. The items ask about "the platform", which non-users cannot evaluate.
- Excluded from A: "No" (non-users) and blank (eligibility unknown). They are described, not analysed.
- Every respondent is in an age band of 18 or over, so no age exclusion is needed.
- Straight-liners (identical answer to all 10 items) and exact duplicate rows are **retained** in A.
  They are suspicious but cannot be shown to be invalid. Their effect is tested in sensitivity analyses.

## 6. Measurement analysis (sample A)
1. Item descriptives: mean, SD, distribution, share of Neutral answers.
2. Two-item reliability: inter-item r, Spearman-Brown coefficient (the recommended index for 2-item
   scales; Eisinga, te Grotenhuis & Pelzer, 2013) and Cronbach's α for comparability.
   Items are **not** dropped to raise reliability.
3. Factorability of the 10 items: KMO and Bartlett's test.
4. Dimensionality: eigenvalues with parallel analysis (1,000 random normal datasets, 95th percentile),
   and the first-factor share of variance (Harman single-factor diagnostic for common-method variance).
5. Discriminant validity: HTMT ratio for each pair of constructs (concern above 0.85, serious above 0.90).

## 7. Hypothesis tests (sample A)
- **Primary test of H1–H4 (association):** Spearman ρ between each construct score and TBCI, with
  bootstrap 95% CIs (5,000 resamples). One-sided direction is pre-specified as positive. P-values are
  Holm-adjusted across the four hypotheses.
  Decision: **supported as an association** if ρ > 0 and Holm-adjusted p < 0.05.
- **Secondary: unique association.** OLS of TBCI on all four construct scores, with HC3 robust SEs,
  standardised β and bootstrap 95% CIs (5,000 resamples), plus VIF. Interpreted as unique association,
  not causal effect.
- **Robustness:** ordinal logistic regression with the same predictors, because TBCI is a 5-point
  ordinal item.
- **H5 and mediation:** not tested (see Section 4). The Q14–Q15 Spearman correlation is reported
  descriptively only.
- **Exploratory:** users versus non-users on each construct score (Mann-Whitney U, rank-biserial
  effect size). Labelled exploratory.

## 8. Sensitivity analyses
- S1: all 112 respondents (users, non-users and blank).
- S2: sample A excluding straight-liners.
- S3: sample A excluding exact duplicate response rows (first occurrence kept).
A conclusion is reported as robust only if its direction and significance hold across A, S2 and S3.

## 9. Deviations from this plan
- None at the time of writing. Any deviation is to be appended here with its reason.

## 10. Power
Sensitivity power analysis for n(A) at α = 0.05 and power 0.80: the smallest detectable f² for the
4-predictor model, and for a single predictor's unique contribution.
