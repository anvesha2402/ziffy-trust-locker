"""Survey analytics engine for the Digital Trust study.

Everything here is plain pandas / numpy / statsmodels so it can be unit-tested
without Streamlit. The Research Lab page is a thin UI over these functions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as sps
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Canonical constructs of the research model (Team Anova, H1–H5)
CONSTRUCTS = {
    "TRN": "Data Transparency",
    "CON": "Consent Mechanisms",
    "GOV": "Governance & Accountability",
    "COM": "Communication",
    "TRU": "Digital Trust",
    "USE": "Continued Usage Intention",
    # constructs used in the Team Anova Google Form instrument
    "PRV": "Privacy & Security",
    "CRD": "Credibility & Social Proof",
    "REL": "Service Reliability",
    "BDM": "Data-Misuse Concern",
    "BCL": "Clinical-Quality Concern",
    "BUS": "Usability Barrier",
    "BFN": "Financial / Payment Concern",
    "BFN": "Financial Concern",
    "GRV": "Complaint Handling",
}
NEGATIVE = {"BDM", "BCL", "BUS", "BFN"}  # barrier constructs: expected to LOWER trust
DRIVERS = ["TRN", "CON", "GOV", "COM"]

HYPOTHESES = [
    ("H1", "TRN", "TRU", "Higher data transparency increases digital trust"),
    ("H2", "CON", "TRU", "Clear, user-friendly consent increases digital trust"),
    ("H3", "GOV", "TRU", "Strong governance & accountability increase digital trust"),
    ("H4", "COM", "TRU", "Clear, timely, empathetic communication increases digital trust"),
    ("H5", "TRU", "USE", "Higher digital trust increases continued usage intention"),
]

_KEYWORDS = {
    "TRN": ["trn", "transp"],
    "CON": ["con", "consent"],
    "GOV": ["gov", "governance", "account"],
    "COM": ["com", "communic"],
    "TRU": ["tru", "trust"],
    "USE": ["use", "usage", "intent", "ci"],
}


# ----------------------------------------------------------------- mapping
def detect_constructs(columns: list[str]) -> dict[str, list[str]]:
    """Guess which columns belong to which construct from their names.

    Works with names like TRN1, trn_2, Transparency_3, "GOV 1", Trust_Q4.
    Ambiguous columns are left unassigned so the user can map them manually.
    """
    mapping: dict[str, list[str]] = {k: [] for k in CONSTRUCTS}
    for col in columns:
        stem = re.sub(r"[\s_\-\.]*(q)?\d+$", "", str(col).strip().lower())
        hits = []
        for code, words in _KEYWORDS.items():
            for w in words:
                if stem == w or (len(w) > 3 and stem.startswith(w)):
                    hits.append(code)
                    break
        if len(hits) == 1:
            mapping[hits[0]].append(col)
    return mapping


def coerce_likert(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Likert text answers ("Strongly agree") to 1–5 numbers."""
    lut = {
        "strongly disagree": 1, "disagree": 2, "neutral": 3,
        "neither agree nor disagree": 3, "agree": 4, "strongly agree": 5,
    }
    out = df.copy()
    for c in out.columns:
        if not pd.api.types.is_numeric_dtype(out[c]):
            mapped = out[c].astype(str).str.strip().str.lower().map(lut)
            if mapped.notna().mean() > 0.8:
                out[c] = mapped
                continue
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


# ------------------------------------------------------------- reliability
def cronbach_alpha(items: pd.DataFrame) -> float:
    items = items.dropna()
    k = items.shape[1]
    if k < 2 or len(items) < 3:
        return float("nan")
    var_sum = items.var(axis=0, ddof=1).sum()
    total_var = items.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return float("nan")
    return float(k / (k - 1) * (1 - var_sum / total_var))


def reliability_table(df: pd.DataFrame, mapping: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    for code, cols in mapping.items():
        if len(cols) < 2:
            continue
        block = df[cols]
        a = cronbach_alpha(block)
        corrected = []
        for c in cols:
            rest = block.drop(columns=c).sum(axis=1)
            corrected.append(block[c].corr(rest))
        if_deleted = {c: cronbach_alpha(block.drop(columns=c)) for c in cols} if len(cols) > 2 else {}
        worst = max(if_deleted, key=if_deleted.get) if if_deleted else None
        rows.append({
            "Construct": CONSTRUCTS.get(code, code),
            "Code": code,
            "Items": len(cols),
            "Cronbach α": round(a, 3),
            "Min item-total r": round(float(np.nanmin(corrected)), 3),
            "α if weakest item dropped": round(if_deleted[worst], 3) if worst else np.nan,
            "Weakest item": worst or "—",
            "Verdict": _alpha_verdict(a),
        })
    return pd.DataFrame(rows)


def _alpha_verdict(a: float) -> str:
    if np.isnan(a):
        return "n/a"
    if a >= 0.9:
        return "Excellent (check redundancy)"
    if a >= 0.8:
        return "Good"
    if a >= 0.7:
        return "Acceptable"
    if a >= 0.6:
        return "Questionable"
    return "Poor – revise scale"


def composites(df: pd.DataFrame, mapping: dict[str, list[str]]) -> pd.DataFrame:
    return pd.DataFrame({code: df[cols].mean(axis=1) for code, cols in mapping.items() if cols})


# ------------------------------------------------------------ correlations
def correlation_matrix(comp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = comp.columns
    r = pd.DataFrame(np.eye(len(cols)), index=cols, columns=cols)
    p = pd.DataFrame(np.zeros((len(cols), len(cols))), index=cols, columns=cols)
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            if j <= i:
                continue
            pair = comp[[a, b]].dropna()
            rr, pp = sps.pearsonr(pair[a], pair[b])
            r.loc[a, b] = r.loc[b, a] = rr
            p.loc[a, b] = p.loc[b, a] = pp
    return r, p


# -------------------------------------------------------------- regression
@dataclass
class RegResult:
    dv: str
    ivs: list[str]
    n: int
    r2: float
    adj_r2: float
    f: float
    f_p: float
    table: pd.DataFrame = field(repr=False)


def regress(comp: pd.DataFrame, dv: str, ivs: list[str]) -> RegResult:
    data = comp[[dv] + ivs].dropna()
    z = (data - data.mean()) / data.std(ddof=1)
    X = sm.add_constant(data[ivs])
    model = sm.OLS(data[dv], X).fit()
    zmodel = sm.OLS(z[dv], sm.add_constant(z[ivs])).fit()
    vifs = {}
    if len(ivs) > 1:
        for i, v in enumerate(ivs, start=1):
            vifs[v] = variance_inflation_factor(X.values, i)
    tbl = pd.DataFrame({
        "Predictor": [CONSTRUCTS.get(v, v) for v in ivs],
        "Code": ivs,
        "B": model.params[ivs].values,
        "SE": model.bse[ivs].values,
        "β (std.)": zmodel.params[ivs].values,
        "t": model.tvalues[ivs].values,
        "p": model.pvalues[ivs].values,
        "VIF": [vifs.get(v, 1.0) for v in ivs],
    })
    return RegResult(dv, ivs, int(model.nobs), float(model.rsquared),
                     float(model.rsquared_adj), float(model.fvalue), float(model.f_pvalue), tbl)


# --------------------------------------------------------------- mediation
@dataclass
class MediationResult:
    x: str
    m: str
    y: str
    a: float
    b: float
    c_total: float
    c_direct: float
    indirect: float
    ci_low: float
    ci_high: float
    n_boot: int
    direct_ci_low: float = float("nan")
    direct_ci_high: float = float("nan")

    @property
    def significant(self) -> bool:
        return not (self.ci_low <= 0 <= self.ci_high)

    @property
    def kind(self) -> str:
        if not self.significant:
            return "No mediation"
        if self.direct_ci_low <= 0 <= self.direct_ci_high:
            return "Full mediation"
        return "Partial mediation"


def mediation(comp: pd.DataFrame, x: str, m: str, y: str,
              n_boot: int = 2000, seed: int = 7) -> MediationResult:
    """Simple mediation X → M → Y with percentile bootstrap CI (Hayes Model 4)."""
    d = comp[[x, m, y]].dropna().to_numpy()
    d = (d - d.mean(0)) / d.std(0, ddof=1)  # standardised paths

    def paths(arr):
        X, M, Y = arr[:, 0], arr[:, 1], arr[:, 2]
        a = np.polyfit(X, M, 1)[0]
        A = np.column_stack([np.ones_like(X), X, M])
        coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
        c_direct, b = coef[1], coef[2]
        c_total = np.polyfit(X, Y, 1)[0]
        return a, b, c_total, c_direct

    a, b, c_total, c_direct = paths(d)
    rng = np.random.default_rng(seed)
    n = len(d)
    boots = np.empty(n_boot)
    direct = np.empty(n_boot)
    for i in range(n_boot):
        s = d[rng.integers(0, n, n)]
        aa, bb, _, cd = paths(s)
        boots[i] = aa * bb
        direct[i] = cd
    lo, hi = np.percentile(boots, [2.5, 97.5])
    dlo, dhi = np.percentile(direct, [2.5, 97.5])
    return MediationResult(x, m, y, a, b, c_total, c_direct, a * b, lo, hi, n_boot, dlo, dhi)


# ---------------------------------------------------------- hypothesis grid
def hypothesis_table(driver_model: RegResult, usage_model: RegResult, alpha: float = 0.05) -> pd.DataFrame:
    rows = []
    lookup = {m.dv: m for m in (driver_model, usage_model)}
    known = {h[1] for h in HYPOTHESES}
    extra = [(f"H{len(HYPOTHESES) + i + 1}", iv, "TRU",
              f"{CONSTRUCTS.get(iv, iv)} {'lowers' if iv in NEGATIVE else 'raises'} digital trust")
             for i, iv in enumerate(v for v in driver_model.ivs if v not in known)]
    for hid, iv, dv, text in HYPOTHESES + extra:
        model = lookup.get(dv)
        if model is None or iv not in model.ivs:
            rows.append({"H": hid, "Path": f"{iv} → {dv}", "Statement": text,
                         "β": np.nan, "p": np.nan, "Result": "Not tested"})
            continue
        row = model.table.set_index("Code").loc[iv]
        sign_ok = row["β (std.)"] < 0 if iv in NEGATIVE else row["β (std.)"] > 0
        ok = row["p"] < alpha and sign_ok
        rows.append({"H": hid, "Path": f"{iv} → {dv}", "Statement": text,
                     "β": round(row["β (std.)"], 3), "p": row["p"],
                     "Result": "Supported" if ok else "Not supported"})
    return pd.DataFrame(rows)


# Keyword map for Google-Form headers ("Section [statement]"), v1 and v2 instruments
FORM_KEYWORDS = [
    ("TRU", ["i trust digital and telehealth", "confident relying on digital", "act in my best interest"]),
    ("PRV", ["kept private", "protected from misuse", "advanced encryption"]),
    ("TRN", ["clearly explain how my health data is used", "which parties (doctor, lab, pharmacy)",
             "who has accessed my health records"]),
    ("CON", ["clear permission before", "withdraw my consent", "which partners (lab, pharmacy, insurer)"]),
    ("GOV", ["who is responsible if my health data", "easy way to raise a complaint",
             "complaints i raise are tracked"]),
    ("COM", ["simple language that i understand", "timely updates at each step", "respectful and caring"]),
    ("CRD", ["certified doctors", "doctor qualifications", "positive reviews", "well-known digital",
             "recommended by friends"]),
    ("REL", ["reliable medical advice", "generally accurate", "without technical glitches"]),
    ("BDM", ["shared without my permission", "sold to third-party"]),
    ("BCL", ["incorrect diagnosis", "lack of physical examination", "symptoms might be missed"]),
    ("BFN", ["online fraud while making payments", "hidden charges"]),
    ("BUS", ["feels complicated", "registration or login process"]),
    ("USE", ["intend to continue using", "recommend digital healthcare services to others",
             "first option for minor health issues"]),
]


def detect_form_constructs(columns: list[str]) -> dict[str, list[str]]:
    """Map long Google-Form question headers to constructs by their statement text.

    Deliberately excludes off-construct or conditional items (pricing clarity,
    'if trust concerns are addressed', 'trust has increased', attention checks).
    """
    mapping: dict[str, list[str]] = {k: [] for k, _ in FORM_KEYWORDS}
    for col in columns:
        low = str(col).lower()
        if "if trust concerns are addressed" in low or "reading carefully" in low:
            continue
        for code, keys in FORM_KEYWORDS:
            if any(k in low for k in keys):
                mapping[code].append(col)
                break
    return {k: v for k, v in mapping.items() if v}


def describe_sample(df: pd.DataFrame, max_levels: int = 8) -> dict[str, pd.Series]:
    """Frequency tables for low-cardinality text columns (demographics)."""
    out = {}
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]) and 1 < df[c].nunique() <= max_levels:
            out[c] = df[c].value_counts(dropna=False)
    return out
