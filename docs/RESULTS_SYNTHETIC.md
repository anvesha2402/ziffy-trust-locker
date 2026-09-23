# Results — synthetic_survey_v2_SYNTHETIC.csv

## Cleaning flow

| Stage                  |   Remaining | Removed (reason)                                   |
|:-----------------------|------------:|:---------------------------------------------------|
| Raw responses          |         262 |                                                    |
| Gave informed consent  |         255 | −7  (declined or blank consent)                    |
| Aged 18+               |         247 | −8  (minors excluded (DPDP s.9 / research ethics)) |
| Past-year users only   |         230 | −17  (non-users cannot rate platform experience)   |
| Passed attention check |         208 | −22  (failed instructed-response item)             |
| No straight-lining     |         206 | −2  (identical answer to every rating item)        |
| ≤10% items missing     |         206 | −0  (too many blanks)                              |

## Quality audit

**FIT FOR ANALYSIS — proceed to reliability and hypothesis testing.**

- PASS · Bartlett's test of sphericity: χ²=2980, df=703, p=7.56e-277
- PASS · Kaiser-Meyer-Olkin (KMO): 0.78
- PASS · Mean |r| vs. shuffled-random data: 0.167 vs 0.059 (random ≥ real in 0% of shuffles)
- PASS · Straight-lining (same answer to every item): 0 of 206
- PASS · Duplicate response patterns: 0
- PASS · Missing values: 0.3%
- PASS · Submission cadence (daily count variation): 14 days, CV=0.93, typical/day=7
- PASS · Respondents under 18: 0
- PASS · Non-users rating platforms: 0

## Reliability

| Construct                   |   Items |   Cronbach α | Verdict             |
|:----------------------------|--------:|-------------:|:--------------------|
| Digital Trust               |       3 |        0.853 | Good                |
| Privacy & Security          |       3 |        0.792 | Acceptable          |
| Data Transparency           |       3 |        0.807 | Good                |
| Consent Mechanisms          |       3 |        0.773 | Acceptable          |
| Governance & Accountability |       3 |        0.823 | Good                |
| Communication               |       3 |        0.851 | Good                |
| Credibility & Social Proof  |       5 |        0.767 | Acceptable          |
| Service Reliability         |       3 |        0.789 | Acceptable          |
| Data-Misuse Concern         |       2 |        0.785 | Acceptable          |
| Clinical-Quality Concern    |       3 |        0.774 | Acceptable          |
| Financial Concern           |       2 |        0.588 | Poor – revise scale |
| Usability Barrier           |       2 |        0.751 | Acceptable          |
| Continued Usage Intention   |       3 |        0.836 | Good                |

## Correlations

|     |   TRU |   PRV |   TRN |   CON |   GOV |   COM |   CRD |   REL |   BDM |   BCL |   BFN |   BUS |   USE |
|:----|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| TRU |  1    |  0.44 |  0.44 |  0.31 |  0.52 |  0.45 |  0.15 |  0.35 | -0.27 | -0.07 | -0.07 | -0.11 |  0.46 |
| PRV |  0.44 |  1    |  0.41 |  0.34 |  0.37 |  0.3  |  0.16 |  0.25 | -0.35 | -0.12 | -0.15 | -0.04 |  0.23 |
| TRN |  0.44 |  0.41 |  1    |  0.33 |  0.24 |  0.37 |  0.17 |  0.32 | -0.21 | -0.06 | -0.05 | -0.14 |  0.19 |
| CON |  0.31 |  0.34 |  0.33 |  1    |  0.27 |  0.16 |  0.03 |  0.22 | -0.15 | -0.07 | -0.06 |  0.02 |  0.18 |
| GOV |  0.52 |  0.37 |  0.24 |  0.27 |  1    |  0.59 |  0.11 |  0.2  | -0.25 | -0.11 | -0.18 | -0.09 |  0.23 |
| COM |  0.45 |  0.3  |  0.37 |  0.16 |  0.59 |  1    |  0.25 |  0.27 | -0.3  | -0.1  | -0.08 | -0.22 |  0.23 |
| CRD |  0.15 |  0.16 |  0.17 |  0.03 |  0.11 |  0.25 |  1    |  0.24 | -0.08 | -0.13 |  0.03 | -0.02 |  0.1  |
| REL |  0.35 |  0.25 |  0.32 |  0.22 |  0.2  |  0.27 |  0.24 |  1    | -0.22 | -0.21 | -0.13 | -0.09 |  0.36 |
| BDM | -0.27 | -0.35 | -0.21 | -0.15 | -0.25 | -0.3  | -0.08 | -0.22 |  1    |  0.07 |  0.09 |  0.11 | -0.17 |
| BCL | -0.07 | -0.12 | -0.06 | -0.07 | -0.11 | -0.1  | -0.13 | -0.21 |  0.07 |  1    | -0.05 | -0.12 | -0.15 |
| BFN | -0.07 | -0.15 | -0.05 | -0.06 | -0.18 | -0.08 |  0.03 | -0.13 |  0.09 | -0.05 |  1    |  0.02 | -0.06 |
| BUS | -0.11 | -0.04 | -0.14 |  0.02 | -0.09 | -0.22 | -0.02 | -0.09 |  0.11 | -0.12 |  0.02 |  1    | -0.17 |
| USE |  0.46 |  0.23 |  0.19 |  0.18 |  0.23 |  0.23 |  0.1  |  0.36 | -0.17 | -0.15 | -0.06 | -0.17 |  1    |

## Model 1 — Trust  (R²=0.435, adj=0.412, F=19.0, n=206)

| Predictor                   | Code   |      B |    SE |   β (std.) |      t |     p |   VIF |
|:----------------------------|:-------|-------:|------:|-----------:|-------:|------:|------:|
| Data Transparency           | TRN    |  0.191 | 0.062 |      0.197 |  3.074 | 0.002 | 1.433 |
| Consent Mechanisms          | CON    |  0.07  | 0.064 |      0.066 |  1.101 | 0.272 | 1.238 |
| Governance & Accountability | GOV    |  0.298 | 0.067 |      0.311 |  4.464 | 0     | 1.698 |
| Communication               | COM    |  0.091 | 0.067 |      0.098 |  1.366 | 0.174 | 1.804 |
| Privacy & Security          | PRV    |  0.158 | 0.069 |      0.149 |  2.281 | 0.024 | 1.49  |
| Credibility & Social Proof  | CRD    | -0.001 | 0.068 |     -0.001 | -0.017 | 0.987 | 1.12  |
| Service Reliability         | REL    |  0.138 | 0.06  |      0.135 |  2.285 | 0.023 | 1.223 |
| Data-Misuse Concern         | BDM    | -0.027 | 0.056 |     -0.029 | -0.488 | 0.626 | 1.217 |

## Model 2 — Usage ~ Trust (R²=0.210)

| Predictor     | Code   |     B |    SE |   β (std.) |     t |   p |   VIF |
|:--------------|:-------|------:|------:|-----------:|------:|----:|------:|
| Digital Trust | TRU    | 0.462 | 0.063 |      0.458 | 7.362 |   0 |     1 |

## Model 3 — Usage ~ Trust + REL + BUS (R²=0.271)

| Predictor           | Code   |      B |    SE |   β (std.) |      t |    p |   VIF |
|:--------------------|:-------|-------:|------:|-----------:|-------:|-----:|------:|
| Digital Trust       | TRU    |  0.371 | 0.065 |      0.367 |  5.719 | 0    | 1.143 |
| Service Reliability | REL    |  0.233 | 0.066 |      0.227 |  3.547 | 0    | 1.138 |
| Usability Barrier   | BUS    | -0.121 | 0.064 |     -0.114 | -1.889 | 0.06 | 1.014 |

## Hypotheses

| H   | Path      | Statement                                                       |      β |      p | Result        |
|:----|:----------|:----------------------------------------------------------------|-------:|-------:|:--------------|
| H1  | TRN → TRU | Higher data transparency increases digital trust                |  0.197 | 0.0024 | Supported     |
| H2  | CON → TRU | Clear, user-friendly consent increases digital trust            |  0.066 | 0.2724 | Not supported |
| H3  | GOV → TRU | Strong governance & accountability increase digital trust       |  0.311 | 0      | Supported     |
| H4  | COM → TRU | Clear, timely, empathetic communication increases digital trust |  0.098 | 0.1736 | Not supported |
| H5  | TRU → USE | Higher digital trust increases continued usage intention        |  0.458 | 0      | Supported     |
| H6  | PRV → TRU | Privacy & Security raises digital trust                         |  0.149 | 0.0236 | Supported     |
| H7  | CRD → TRU | Credibility & Social Proof raises digital trust                 | -0.001 | 0.9868 | Not supported |
| H8  | REL → TRU | Service Reliability raises digital trust                        |  0.135 | 0.0234 | Supported     |
| H9  | BDM → TRU | Data-Misuse Concern lowers digital trust                        | -0.029 | 0.6262 | Not supported |

## Mediation (5,000 bootstrap)

- Data Transparency → Trust → Usage: indirect=0.203 [0.127, 0.302], direct=-0.009 [-0.156, 0.135] → Full mediation
- Consent Mechanisms → Trust → Usage: indirect=0.140 [0.074, 0.220], direct=0.036 [-0.085, 0.160] → Full mediation
- Governance & Accountability → Trust → Usage: indirect=0.243 [0.157, 0.339], direct=-0.009 [-0.144, 0.128] → Full mediation
- Communication → Trust → Usage: indirect=0.202 [0.124, 0.289], direct=0.028 [-0.100, 0.156] → Full mediation

## Sample profile

- Age: 18-24 73, 25-34 67, 35-44 34, 45-54 21, 55-64 7, 65 and over 4
- Location: Metro city 92, Tier-2 / Tier-3 city 80, Rural / semi-urban 34
- Preferred language: English 82, Hindi 69, Marathi 40, Other 15
- Platform: Apollo 24|7 51, Practo 48, Tata 1mg 40, PharmEasy 28, Hospital's own app 21, Other 9, eSanjeevani 9
- Usage frequency: A few times a year 72, Monthly 71, Weekly 46, Daily/Almost Daily 17

## Business case (default assumptions)

- Pilot+scale: NPV ₹7.0 L, payback month 27, gain/cost 1.27×, break-even uplift 1.8 pp, P(NPV>0)=53%
- Pilot only: NPV ₹-11.6 L, payback None, gain/cost 0.61×
