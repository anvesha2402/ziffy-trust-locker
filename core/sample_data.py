"""Synthetic datasets for the Digital Trust study (Team Anova × ZiffyHealth).

READ THIS FIRST
---------------
Every dataset produced here is SYNTHETIC. It is not the Team Anova survey and
must never be presented as real respondents' answers. It exists so the
analysis pipeline, the Streamlit app and the case study can be demonstrated
end-to-end and re-run by anyone.

What it replicates, and what it fixes
-------------------------------------
It mirrors the Team Anova Google Form (same sections, statements and Likert
wording, same Google-Forms export layout) as *Instrument v2*, which corrects
the problems found in the original data audit:

1. Every hypothesised construct is measured with ≥3 items. The original form had
   no Governance or Communication scales even though H3/H4 tested them.
2. Off-construct items are separated (pricing clarity is no longer inside
   "Data Privacy & Transparency"; "trust increased with experience" and the
   conditional "if concerns are addressed" item are no longer mixed into
   Usage Intention).
3. Screening: informed consent, 18+ only, and past-year users only, with
   branching, so minors and non-users never reach the rating questions.
4. "None of the above" is exclusive in the services question.
5. An attention-check item is included, and a small realistic share of
   careless responders (random clickers, straight-liners) is simulated so the
   cleaning pipeline has something real to catch.
6. Organic, bursty submission timing (share waves on WhatsApp / LinkedIn)
   instead of a flat 20 responses per day.
7. An underlying causal structure (a latent-variable model) so items within a
   construct correlate, and the relationships are of plausible size.

Ground truth (latent model, standardised)
-----------------------------------------
TRU = .20·TRN + .17·CON + .18·GOV + .14·COM + .18·PRV + .07·CRD + .11·REL − .10·BDM + ε
USE = .52·TRU + .10·REL − .12·BUS + ε
Rural / semi-urban respondents: lower TRN, higher BUS. Age 55+: higher BUS.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

LIKERT = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]

# construct code -> (Google Form section title, [statements])
SECTIONS: dict[str, tuple[str, list[str]]] = {
    "TRU": ("Overall Trust in Digital Healthcare Services", [
        "I trust digital and telehealth services for managing my healthcare needs.",
        "I feel confident relying on digital healthcare services when medical help is needed.",
        "I believe that digital healthcare providers generally act in my best interest regarding my health.",
    ]),
    "PRV": ("Trust-Building Factors: Data Privacy and Security", [
        "I believe my personal health information is kept private on digital healthcare platforms.",
        "I feel my health data is protected from misuse or cyberattacks.",
        "I am confident that the platform uses advanced encryption (secure technology) to store my medical records.",
    ]),
    "TRN": ("Trust-Building Factors: Data Transparency", [
        "Digital healthcare platforms clearly explain how my health data is used.",
        "I can see which parties (doctor, lab, pharmacy) my health data is shared with.",
        "I can see who has accessed my health records and when.",
    ]),
    "CON": ("Trust-Building Factors: Consent and Control", [
        "I am asked for clear permission before my health data is collected or shared.",
        "I feel confident that I can withdraw my consent or delete my data from the platform whenever I choose.",
        "I can choose which partners (lab, pharmacy, insurer) are allowed to see my data.",
    ]),
    "GOV": ("Trust-Building Factors: Governance and Accountability", [
        "It is clear who is responsible if my health data is misused.",
        "There is an easy way to raise a complaint about my data or my care.",
        "Complaints I raise are tracked and resolved within a reasonable time.",
    ]),
    "COM": ("Trust-Building Factors: Communication", [
        "The platform explains things in simple language that I understand.",
        "I receive timely updates at each step of my care (e.g., report ready, medicine dispatched).",
        "Messages from the platform feel respectful and caring.",
    ]),
    "CRD": ("Trust-Building Factors: Credibility and Social Proof", [
        "I trust digital healthcare services that are associated with certified doctors or hospitals.",
        "Seeing doctor qualifications on digital platforms increases my trust.",
        "Positive reviews and ratings from other patients significantly increase my trust in a digital doctor.",
        "Well-known digital healthcare platforms appear more trustworthy to me.",
        "I am more likely to trust a digital healthcare platform if it is recommended by friends or family.",
    ]),
    "REL": ("Trust-Building Factors: Service Reliability", [
        "Digital healthcare platforms provide reliable medical advice.",
        "Online consultations through digital healthcare are generally accurate.",
        "I trust that the platform will function smoothly without technical glitches (e.g., video freezing) during consultations.",
    ]),
    "BDM": ("Trust Barriers / Concerns", [
        "I worry that my health data may be shared without my permission.",
        "I worry that my health data might be sold to third-party companies (like insurance or pharmaceutical firms) without my knowledge.",
    ]),
    "BCL": ("Trust Barriers / Concerns", [
        "I am concerned about incorrect diagnosis through online consultations.",
        "The lack of physical examination reduces my trust in digital healthcare services.",
        "I am concerned that important physical symptoms might be missed because the doctor cannot see me clearly through a screen.",
    ]),
    "BFN": ("Trust Barriers / Concerns", [
        "I fear online fraud while making payments on digital healthcare platforms.",
        "Hidden charges reduce my trust in digital healthcare services.",
    ]),
    "BUS": ("Trust Barriers / Concerns", [
        "Using digital healthcare platforms feels complicated for me.",
        "I find the registration or login process for digital health apps frustrating, which lowers my trust in them.",
    ]),
    "USE": ("Future Intention and Adoption", [
        "I intend to continue using digital healthcare services in the future.",
        "I would recommend digital healthcare services to others.",
        "I plan to make digital healthcare my first option for minor health issues before visiting a physical clinic.",
    ]),
}
ATTENTION = ("Trust Barriers / Concerns",
             "To show you are reading carefully, please select 'Agree' for this statement.")
PRICING = ("Pricing", "The pricing of digital healthcare services is clear and upfront.")
CONDITIONAL = ("Future Intention and Adoption",
               "I am willing to use digital healthcare services more frequently if trust concerns are addressed.")

SERVICES = ["Online doctor consultations (video/chat)", "Online prescription refills/pharmacy services",
            "Viewing lab results/medical records online", "Scheduling appointments online",
            "Digital health monitoring apps (e.g. BP, fitness)", "Mental health/counselling via telehealth"]
PLATFORMS = ["Practo", "Apollo 24|7", "Tata 1mg", "PharmEasy", "eSanjeevani", "Hospital's own app", "Other"]

Q_CONSENT = "I have read the participant information and agree to take part in this survey."
Q_AGE = "Please provide the age range you belong to:"
Q_LOC = "Where do you live?"
Q_LANG = "Which language do you prefer for health information?"
Q_SERV = "Which of the following digital healthcare services have you used in the past year?"
Q_FREQ = "How often do you use digital healthcare services?"
Q_PLAT = "Which platform do you use most often?"
Q_EXP = "Your overall experience with digital healthcare services can be rated as:"


def header(code: str, i: int) -> str:
    sec, items = SECTIONS[code]
    return f"{sec} [{items[i]}]"


def item_columns() -> dict[str, list[str]]:
    return {c: [header(c, i) for i in range(len(SECTIONS[c][1]))] for c in SECTIONS}


def _to_likert(latent: np.ndarray, rng, loading: float) -> np.ndarray:
    x = loading * latent + np.sqrt(1 - loading ** 2) * rng.normal(size=latent.shape)
    cuts = np.array([-1.55, -0.75, 0.05, 1.05])  # slightly agree-skewed, like real surveys
    return np.searchsorted(cuts, x)  # 0..4


def _timestamps(n: int, rng, start=datetime(2026, 1, 21, 9, 0)) -> list[datetime]:
    """Bursty arrivals: a few share waves, decaying over ~2 days each, evening-heavy."""
    waves = [(0.0, .30), (2.3, .22), (5.1, .18), (8.4, .16), (10.2, .14)]  # (day offset, share)
    out = []
    for _ in range(n):
        d0, _ = waves[rng.choice(len(waves), p=[w[1] for w in waves])]
        lag_h = rng.exponential(14)
        hour_bias = rng.choice([0, 3, 6, 10, 12], p=[.15, .15, .2, .3, .2])
        out.append(start + timedelta(days=d0, hours=lag_h + hour_bias, minutes=int(rng.integers(0, 60)),
                                     seconds=int(rng.integers(0, 60))))
    return sorted(out)


def synthetic_survey(n_raw: int = 262, seed: int = 2026) -> pd.DataFrame:
    """Return a Google-Forms-style export (text Likert answers), including
    screened-out and careless rows so the cleaning pipeline can be demonstrated."""
    rng = np.random.default_rng(seed)

    # --- screening & profile -------------------------------------------------
    consent = rng.choice(["Yes", "No"], n_raw, p=[.975, .025])
    age = rng.choice(["Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65 and over"], n_raw,
                     p=[.03, .36, .30, .14, .09, .05, .03])
    loc = rng.choice(["Metro city", "Tier-2 / Tier-3 city", "Rural / semi-urban"], n_raw, p=[.58, .29, .13])
    lang = np.where(loc == "Metro city", rng.choice(["English", "Hindi", "Marathi", "Other"], n_raw, p=[.62, .2, .12, .06]),
                    rng.choice(["English", "Hindi", "Marathi", "Other"], n_raw, p=[.25, .45, .22, .08]))
    nonuser = rng.random(n_raw) < 0.06
    services, freq, plat = [], [], []
    for i in range(n_raw):
        if nonuser[i]:
            services.append("None of the above")
            freq.append("")
            plat.append("")
            continue
        k = int(rng.choice([1, 2, 3, 4], p=[.3, .35, .22, .13]))
        pick = rng.choice(SERVICES, k, replace=False, p=[.3, .22, .18, .16, .1, .04])
        services.append(", ".join(pick))
        freq.append(rng.choice(["Daily/Almost Daily", "Weekly", "Monthly", "A few times a year"], p=[.08, .2, .34, .38]))
        plat.append(rng.choice(PLATFORMS, p=[.24, .2, .2, .12, .07, .12, .05]))

    rural = (loc == "Rural / semi-urban").astype(float)
    older = np.isin(age, ["55-64", "65 and over"]).astype(float)

    # --- latent drivers --------------------------------------------------------
    names = ["TRN", "CON", "GOV", "COM", "PRV", "CRD", "REL"]
    R = np.array([
        [1.00, .45, .40, .42, .45, .20, .30],
        [.45, 1.00, .42, .35, .40, .15, .25],
        [.40, .42, 1.00, .65, .50, .20, .30],
        [.42, .35, .65, 1.00, .35, .25, .38],
        [.45, .40, .50, .35, 1.00, .22, .30],
        [.20, .15, .20, .25, .22, 1.00, .35],
        [.30, .25, .30, .38, .30, .35, 1.00],
    ])
    L = dict(zip(names, rng.multivariate_normal(np.zeros(7), R, n_raw).T))
    L["TRN"] = L["TRN"] - 0.35 * rural
    L["BDM"] = -0.45 * L["PRV"] + np.sqrt(1 - .45 ** 2) * rng.normal(size=n_raw)
    L["BCL"] = -0.35 * L["REL"] + np.sqrt(1 - .35 ** 2) * rng.normal(size=n_raw)
    L["BFN"] = -0.25 * L["PRV"] + np.sqrt(1 - .25 ** 2) * rng.normal(size=n_raw)
    L["BUS"] = 0.45 * rural + 0.55 * older - 0.2 * L["COM"] + rng.normal(0, .9, n_raw)
    tru = (.20 * L["TRN"] + .17 * L["CON"] + .18 * L["GOV"] + .14 * L["COM"] + .18 * L["PRV"]
           + .07 * L["CRD"] + .11 * L["REL"] - .10 * L["BDM"])
    tru = tru + rng.normal(0, 0.62, n_raw)
    L["TRU"] = (tru - tru.mean()) / tru.std()
    use = .52 * L["TRU"] + .10 * L["REL"] - .12 * L["BUS"] + rng.normal(0, .78, n_raw)
    L["USE"] = (use - use.mean()) / use.std()

    loadings = {"TRU": .84, "PRV": .80, "TRN": .78, "CON": .77, "GOV": .79, "COM": .80, "CRD": .66,
                "REL": .74, "BDM": .86, "BCL": .72, "BFN": .66, "BUS": .84, "USE": .82}

    data: dict[str, list | np.ndarray] = {}
    data["Timestamp"] = _timestamps(n_raw, rng)
    data[Q_CONSENT] = consent
    data[Q_AGE] = age
    data[Q_LOC] = loc
    data[Q_LANG] = lang
    data[Q_SERV] = services
    data[Q_FREQ] = freq
    data[Q_PLAT] = plat
    codes = {}
    for code in SECTIONS:
        for i, col in enumerate(item_columns()[code]):
            codes[col] = _to_likert(L[code], rng, loadings[code])
    # pricing (weakly related to trust & financial barrier), conditional usage
    pr = _to_likert(0.25 * L["TRU"] - 0.3 * L["BFN"] + rng.normal(0, .9, n_raw), rng, .75)
    cond = _to_likert(0.35 * L["USE"] + 0.3 * L["BDM"] + rng.normal(0, .85, n_raw), rng, .75)
    att = np.full(n_raw, 3)
    exp_ = np.clip(np.round(3.2 + 0.55 * L["TRU"] + 0.35 * L["REL"] + rng.normal(0, .6, n_raw)), 1, 5).astype(int)

    # --- careless responders ----------------------------------------------------
    careless = rng.random(n_raw)
    random_clickers = careless < 0.045
    straight = (careless >= 0.045) & (careless < 0.075)
    all_cols = list(codes)
    for i in np.where(random_clickers)[0]:
        for c in all_cols:
            codes[c][i] = rng.integers(0, 5)
        pr[i], cond[i], att[i] = rng.integers(0, 5, 3)
        if att[i] == 3:            # a random clicker may pass the check by luck
            att[i] = rng.choice([0, 1, 2, 4])
    for i in np.where(straight)[0]:
        v = rng.choice([2, 3, 4])
        for c in all_cols:
            codes[c][i] = v
        pr[i] = cond[i] = att[i] = v

    for c in all_cols:
        data[c] = codes[c]
    data[f"{ATTENTION[0]} [{ATTENTION[1]}]"] = att
    data[f"{PRICING[0]} [{PRICING[1]}]"] = pr
    data[f"{CONDITIONAL[0]} [{CONDITIONAL[1]}]"] = cond
    data[Q_EXP] = exp_
    df = pd.DataFrame(data)

    # Likert codes -> Google Forms text
    lik_cols = all_cols + [f"{ATTENTION[0]} [{ATTENTION[1]}]", f"{PRICING[0]} [{PRICING[1]}]",
                           f"{CONDITIONAL[0]} [{CONDITIONAL[1]}]"]
    for c in lik_cols:
        df[c] = df[c].map(dict(enumerate(LIKERT)))

    # Branching: screened-out respondents never saw the rating pages
    screened = (df[Q_CONSENT] == "No") | (df[Q_AGE] == "Under 18") | (df[Q_SERV] == "None of the above")
    df.loc[screened, lik_cols + [Q_EXP, Q_FREQ, Q_PLAT]] = np.nan
    df.loc[df[Q_CONSENT] == "No", [Q_AGE, Q_LOC, Q_LANG, Q_SERV]] = np.nan
    df.loc[df[Q_AGE] == "Under 18", [Q_LOC, Q_LANG, Q_SERV]] = np.nan

    # a sprinkle of item non-response (~0.4%)
    mask = rng.random((len(df), len(all_cols))) < 0.004
    sub = df[all_cols].mask(mask)
    df[all_cols] = sub
    df[Q_EXP] = df[Q_EXP].astype("Int64")
    return df


def data_card() -> str:
    return (
        "SYNTHETIC DATA — NOT REAL RESPONDENTS\n"
        "Generated by core/sample_data.py (seed 2026) to demonstrate the Team Anova × ZiffyHealth "
        "digital-trust analysis pipeline. It mirrors the survey instrument (v2, corrected) and "
        "follows a documented latent-variable model. Any statistic computed from it describes the "
        "simulation, not Indian digital-health users.\n"
    )


# ------------------------------------------------------------------ Kano
KANO_FEATURES = [
    "Multilingual consent wizard",
    "Doctor identity card",
    "Plain-language access log",
    "Per-partner consent toggles",
    "Care Moments (WhatsApp/SMS)",
    "Grievance with case ID",
    "Audio narration at kiosk",
    "Download / share my records (ABHA)",
    "Trust status panel",
    "Data deletion request",
]
ANSWERS = ["Like", "Expect", "Neutral", "Live with", "Dislike"]
_PROFILES = {
    "Multilingual consent wizard": "M", "Doctor identity card": "O",
    "Plain-language access log": "A", "Per-partner consent toggles": "O",
    "Care Moments (WhatsApp/SMS)": "O", "Grievance with case ID": "M",
    "Audio narration at kiosk": "A", "Download / share my records (ABHA)": "O",
    "Trust status panel": "I", "Data deletion request": "A",
}
_F = {"M": [.15, .55, .2, .07, .03], "O": [.7, .15, .1, .03, .02],
      "A": [.65, .05, .22, .06, .02], "I": [.25, .1, .5, .12, .03]}
_D = {"M": [.02, .03, .1, .15, .7], "O": [.02, .03, .1, .15, .7],
      "A": [.02, .03, .55, .3, .1], "I": [.02, .05, .55, .3, .08]}


def demo_kano(n: int = 110, seed: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for r in range(n):
        for f in KANO_FEATURES:
            prof = _PROFILES[f]
            rows.append({"respondent_id": f"K{r:03d}", "feature": f,
                         "functional": rng.choice(ANSWERS, p=_F[prof]),
                         "dysfunctional": rng.choice(ANSWERS, p=_D[prof])})
    return pd.DataFrame(rows)


def questionnaire() -> pd.DataFrame:
    rows = []
    for code, (sec, items) in SECTIONS.items():
        for i, s in enumerate(items, 1):
            rows.append({"Code": f"{code}{i}", "Section": sec, "Statement": s, "Scale": "5-pt Likert"})
    rows += [{"Code": "ATT1", "Section": ATTENTION[0], "Statement": ATTENTION[1], "Scale": "Attention check"},
             {"Code": "PRC1", "Section": PRICING[0], "Statement": PRICING[1], "Scale": "5-pt Likert"},
             {"Code": "USEC", "Section": CONDITIONAL[0], "Statement": CONDITIONAL[1], "Scale": "5-pt Likert (separate outcome)"}]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parents[1] / "data"
    df = synthetic_survey()
    df.to_csv(out / "synthetic_survey_v2_SYNTHETIC.csv", index=False)
    with pd.ExcelWriter(out / "synthetic_survey_v2_SYNTHETIC.xlsx") as xw:
        df.to_excel(xw, sheet_name="Form responses 1", index=False)
        pd.DataFrame({"README": data_card().splitlines()}).to_excel(xw, sheet_name="READ ME", index=False)
    demo_kano().to_csv(out / "kano_responses_SYNTHETIC.csv", index=False)
    questionnaire().to_csv(out / "questionnaire_v2.csv", index=False)
    print(df.shape, "written to", out)
