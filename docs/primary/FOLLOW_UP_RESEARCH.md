# Follow-up research plan

The primary survey shows **associations** between users' views of four data practices and a single-item
trust-based continuance intention. It cannot show whether trust drives use, whether the Locker would change
anything, or whether results hold for e-clinic patients. Three studies close those gaps. None of them has been
run; nothing here reports results.

| Gap (see [LIMITATIONS_REGISTER](../LIMITATIONS_REGISTER.md)) | Study |
|---|---|
| No separate trust or intention measure; H5 and mediation untestable (C1) | Study 1 |
| E-clinic persona not sampled (B2, B3) | Study 1 (stratified intercept) |
| Constructs not distinct; 2 items each (C3, C4) | Study 1 (3 items each, CFA) |
| No Kano data (G1) | Study 1, Kano block |
| No usability or accessibility evidence (F6) | Study 2 |
| Business value levers unverified (D1, D2) | Study 3 |

## 1. Study 1: intercept survey at e-clinics and online

- **Population.** Adults who used a digital-health service in the last 12 months, in two strata: (a) e-clinic kiosk
  patients, intercepted after the consultation with operator help offered; (b) app and tele-consultation users,
  recruited online.
- **Sample size.** At least 200 completed responses per stratum. That gives 80% power to detect a correlation of
  0.20 (n = 194, two-sided α = 0.05), and is a common minimum for a confirmatory factor analysis with six
  three-item constructs.
- **Instrument.** Section 3 below. Hindi and Marathi translation with independent back-translation; cognitive
  pre-test with 5–8 respondents per language before fielding.
- **Design controls.** Outcome block (trust, continuance intention) asked before the driver blocks, to reduce
  consistency effects; items randomised within blocks; all items exported as text labels to avoid the mixed-format
  problem of the first survey.
- **Pre-registered analysis.** CFA (target CFI ≥ 0.95, SRMR ≤ 0.08), HTMT < 0.85 for discriminant validity, then
  structural model TRN, CON, GOV, COM → TRU → CI with bootstrap indirect effects; multi-group comparison by stratum;
  Q15 as a moderator. Hypotheses and decision rules fixed before data collection, as in
  [ANALYSIS_PLAN](ANALYSIS_PLAN.md).
- **Ethics.** Informed consent screen, no names, no health conditions asked, data stored in India, deletion on request.

## 2. Study 2: usability test of the Locker prototype

- **Participants.** 5–8 per persona per language (e.g., semi-urban Hindi-first assisted user; urban English app user).
- **Tasks.** Complete the kiosk consent; find who viewed a lab report; switch off pharmacy access; raise a
  complaint and find its case number.
- **Measures.** Task success, time on task, errors, System Usability Scale, think-aloud comments, comprehension
  check of what was consented to.
- **Accessibility.** Screen-reader and contrast check (WCAG 2.2 AA), audio narration test with low-literacy users.

## 3. Study 3: pilot evaluation design

- **Design.** Matched-clinic difference-in-differences: Locker clinics vs comparable clinics without it, matched
  on footfall, location type and baseline repeat rate, with 3 months of pre-period data. If rollout is phased,
  a stepped-wedge design (clinics switch on in random order) strengthens the comparison.
- **Primary outcomes.** 90-day repeat-visit rate (EHR); status calls per patient (call logs).
- **Secondary outcomes.** Consent completion and time at the kiosk; Locker views; consent withdrawals; grievances
  and resolution time; trust and continuance intention (Study 1 instrument, exit survey).
- **Scale needed.** Detecting a 3-percentage-point rise in repeat visits from a 30% baseline needs about 3,760
  patients per arm if patients were independent (two-sided α = 0.05, power 0.80); clustering by clinic raises this
  by the design effect, so the pilot must be large enough or treat repeat visits as a secondary, descriptive outcome.
  A 5-point rise needs about 1,380 per arm before clustering.
- **Decision rule (set before launch).** Scale only if call deflection and repeat-visit change both exceed the
  break-even values in the ROI model computed with actual pilot costs.

## 4. Follow-up instrument

Machine-readable copy: [`data/primary/follow_up_instrument.csv`](../../data/primary/follow_up_instrument.csv). Items marked *Original* keep the exact wording of the first survey so results can be compared.

| Code   | Block                      | Statement                                                                                           | Response format                                                                                                 | Origin                                                             |
|:-------|:---------------------------|:----------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------|
| SCR1   | Screening                  | I have read the information above and agree to take part.                                           | Yes / No (No ends the form)                                                                                     | New                                                                |
| SCR2   | Screening                  | Are you 18 years or older?                                                                          | Yes / No (No ends the form)                                                                                     | New                                                                |
| SCR3   | Screening                  | In the last 12 months, which of these have you used? (tick all)                                     | E-clinic kiosk · tele-consultation app · online lab booking · online pharmacy · none (exclusive; ends the form) | New                                                                |
| SCR4   | Screening                  | Which platform will you answer about? (the one you used most recently)                              | Ziffy e-clinic / ZiffyHealth app · other (name)                                                                 | New                                                                |
| CTX1   | Context                    | Where do you live?                                                                                  | Metro · other city · small town · village                                                                       | New                                                                |
| CTX2   | Context                    | Which language do you prefer for health information?                                                | English · Hindi · Marathi · other                                                                               | New                                                                |
| CTX3   | Context                    | Did a kiosk operator or staff member help you use the service?                                      | Yes / No / Not applicable                                                                                       | New                                                                |
| CTX4   | Context                    | How confident are you filling out medical forms by yourself?                                        | 5-pt: not at all … extremely (single-item literacy screener)                                                    | New                                                                |
| CTX5   | Context                    | Age band, gender, occupation                                                                        | As in the original form                                                                                         | Original                                                           |
| Q6     | Transparency (TRN)         | I clearly understand how my health data is collected and used by the digital healthcare platform.   | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original                                                           |
| Q7     | Transparency (TRN)         | The platform is transparent about who can access my health data and when it is shared.              | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original                                                           |
| TRN3   | Transparency (TRN)         | I can see who has viewed my health records and when.                                                | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| Q8     | Consent (CON)              | The consent process allows me to clearly choose what type of health data I want to share.           | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original                                                           |
| Q9     | Consent (CON)              | I feel confident using the platform because I can easily withdraw or modify my consent at any time. | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original                                                           |
| CON3   | Consent (CON)              | I am asked before my health data is shared with a lab, pharmacy or insurer.                         | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| Q10    | Governance (GOV)           | I believe the platform has strong measures in place to protect my health data from misuse.          | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original (export as text, not number)                              |
| Q11r   | Governance (GOV)           | The platform would take responsibility and address issues if my data were misused.                  | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Reworded: 'I trust that' removed to avoid overlap with trust items |
| GOV3   | Governance (GOV)           | If I raised a complaint about my data, it would be tracked and answered.                            | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| Q12    | Communication (COM)        | The platform communicates clearly and in a timely manner about matters related to my health data.   | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original                                                           |
| Q13    | Communication (COM)        | The platform's communication makes me feel informed and reassured about my data and services.       | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original                                                           |
| COM3   | Communication (COM)        | I receive an update at each step of my care (for example, report ready, prescription sent).         | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| ATT1   | Attention check            | To show you are reading carefully, please select 'Disagree' for this statement.                     | Pass = Disagree                                                                                                 | New                                                                |
| TRU1   | Digital trust (TRU)        | I trust this platform with my health information.                                                   | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New (direct trust measure)                                         |
| TRU2   | Digital trust (TRU)        | This platform is honest about how it handles my health data.                                        | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| TRU3   | Digital trust (TRU)        | I can rely on this platform to act in my interest when it handles my data.                          | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| CI1    | Continuance intention (CI) | I intend to continue using this platform for my healthcare needs.                                   | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New (separates intention from trust; replaces Q14 as outcome)      |
| CI2    | Continuance intention (CI) | I will use this platform again the next time I need a consultation or test.                         | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| CI3    | Continuance intention (CI) | I would choose this platform over other ways of getting the same care.                              | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | New                                                                |
| Q14    | Comparison item            | Because I trust the platform, I intend to continue using it for my healthcare needs.                | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original; kept for comparison with the first survey                |
| Q15    | Importance of trust        | My level of trust strongly influences my decision to keep using a digital healthcare platform.      | 5-pt labelled (Strongly disagree … Strongly agree)                                                              | Original; analysed as a separate (moderator) variable              |
| KF1    | Kano (functional)          | If the service had: plain-language access log — how would you feel?                                 | I like it · I expect it · I am neutral · I can tolerate it · I dislike it                                       | New                                                                |
| KD1    | Kano (dysfunctional)       | If the service did NOT have: plain-language access log — how would you feel?                        | Same five options                                                                                               | New                                                                |
| KF2    | Kano (functional)          | If the service had: per-partner consent switches — how would you feel?                              | I like it · I expect it · I am neutral · I can tolerate it · I dislike it                                       | New                                                                |
| KD2    | Kano (dysfunctional)       | If the service did NOT have: per-partner consent switches — how would you feel?                     | Same five options                                                                                               | New                                                                |
| KF3    | Kano (functional)          | If the service had: doctor identity card at the kiosk — how would you feel?                         | I like it · I expect it · I am neutral · I can tolerate it · I dislike it                                       | New                                                                |
| KD3    | Kano (dysfunctional)       | If the service did NOT have: doctor identity card at the kiosk — how would you feel?                | Same five options                                                                                               | New                                                                |
| KF4    | Kano (functional)          | If the service had: step-by-step care updates on whatsapp/sms — how would you feel?                 | I like it · I expect it · I am neutral · I can tolerate it · I dislike it                                       | New                                                                |
| KD4    | Kano (dysfunctional)       | If the service did NOT have: step-by-step care updates on whatsapp/sms — how would you feel?        | Same five options                                                                                               | New                                                                |
| KF5    | Kano (functional)          | If the service had: complaint with a case number and deadline — how would you feel?                 | I like it · I expect it · I am neutral · I can tolerate it · I dislike it                                       | New                                                                |
| KD5    | Kano (dysfunctional)       | If the service did NOT have: complaint with a case number and deadline — how would you feel?        | Same five options                                                                                               | New                                                                |
| KF6    | Kano (functional)          | If the service had: consent explained by audio in my language — how would you feel?                 | I like it · I expect it · I am neutral · I can tolerate it · I dislike it                                       | New                                                                |
| KD6    | Kano (dysfunctional)       | If the service did NOT have: consent explained by audio in my language — how would you feel?        | Same five options                                                                                               | New                                                                |

Sources for adapted items: trust items follow the trusting-beliefs dimensions (competence, integrity, benevolence) of McKnight, Choudhury and Kacmar (2002); continuance-intention items follow Bhattacherjee (2001); Kano question format follows Berger et al. (1993). Wording is the team's adaptation and must be pre-tested.
