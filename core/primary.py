"""Primary survey analysis: genuine Team Anova responses (n = 112).

Implements docs/primary/ANALYSIS_PLAN.md exactly. Every number published from the primary survey
(report, case study, app, README) is produced by this module via scripts/primary_analysis.py.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

RAW_SHA256 = "d681ca838d795e3f3166579e97385f1bb3b96349626919ad6a69a9a38b445230"
DEID_PATH = Path(__file__).resolve().parents[1] / "data" / "primary" / "primary_survey_deidentified.csv"

LIKERT = {"strongly disagree": 1, "disagree": 2, "neutral": 3, "agree": 4, "strongly agree": 5}

ITEMS = {
    "Q6": "I clearly understand how my health data is collected and used by the digital healthcare platform.",
    "Q7": "The platform is transparent about who can access my health data and when it is shared.",
    "Q8": "The consent process allows me to clearly choose what type of health data I want to share.",
    "Q9": "I feel confident using the platform because I can easily withdraw or modify my consent at any time.",
    "Q10": "I believe the platform has strong measures in place to protect my health data from misuse.",
    "Q11": "I trust that the platform would take responsibility and address issues if my data were misused.",
    "Q12": "The platform communicates clearly and in a timely manner about matters related to my health data.",
    "Q13": "The platform's communication makes me feel informed and reassured about my data and services.",
    "Q14": "Because I trust the platform, I intend to continue using it for my healthcare needs.",
    "Q15": "My level of trust strongly influences my decision to keep using a digital healthcare platform.",
}
NUMERIC_EXPORT = ["Q10", "Q12", "Q14", "Q15"]  # exported by Google Forms as 1–5 numbers
CONSTRUCTS = {
    "TRN": ("Data transparency", ["Q6", "Q7"], "H1"),
    "CON": ("Consent mechanisms", ["Q8", "Q9"], "H2"),
    "GOV": ("Governance & accountability", ["Q10", "Q11"], "H3"),
    "COM": ("Communication", ["Q12", "Q13"], "H4"),
}
OUTCOME = "Q14"            # trust-based continuance intention (TBCI)
IMPORTANCE = "Q15"         # perceived importance of trust
DRIVERS = list(CONSTRUCTS)


# ------------------------------------------------------------------ load / de-identify
def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def deidentify(raw_xlsx: str | Path) -> pd.DataFrame:
    """Raw Google-Forms export -> de-identified, coded dataframe (no names, date only)."""
    raw = pd.read_excel(raw_xlsx)
    cols = list(raw.columns)
    assert len(cols) == 16, "unexpected column count"
    ts = pd.to_datetime(raw[cols[0]])
    order = ts.sort_values(kind="stable").index
    raw = raw.loc[order].reset_index(drop=True)
    ts = ts.loc[order].reset_index(drop=True)
    out = pd.DataFrame({
        "response_id": [f"R{i:03d}" for i in range(1, len(raw) + 1)],
        "response_date": ts.dt.date.astype(str),
        "gender": raw[cols[2]].astype(str).str.strip(),
        "age_band": raw[cols[3]].astype(str).str.strip(),
        "profession": raw[cols[4]].astype(str).str.strip(),
        "used_digital_health": raw[cols[5]].astype(str).str.strip().replace({"": "(blank)", "nan": "(blank)"}),
    })
    for i, q in enumerate(ITEMS, start=6):
        out[q] = code_item(raw[cols[i]])
    return out


def code_item(s: pd.Series) -> pd.Series:
    t = s.astype(str).str.strip().str.lower()
    num = pd.to_numeric(t, errors="coerce")
    coded = num.where(num.notna(), t.map(LIKERT))
    return coded.astype("Int64")


def load() -> pd.DataFrame:
    df = pd.read_csv(DEID_PATH)
    for q in ITEMS:
        df[q] = df[q].astype(float)
    return df


# ------------------------------------------------------------------ samples
def samples(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    users = df[df["used_digital_health"] == "Yes"]
    X = users[list(ITEMS)]
    straight = X.nunique(axis=1) == 1
    dup = X.duplicated(keep="first")
    return {
        "A": users,
        "S1": df,
        "S2": users[~straight],
        "S3": users[~dup],
    }


def flow(df: pd.DataFrame) -> pd.DataFrame:
    users = df[df["used_digital_health"] == "Yes"]
    X = users[list(ITEMS)]
    rows = [
        ("Responses in file", len(df), ""),
        ("Missing item responses", int(df[list(ITEMS)].isna().sum().sum()), "cells"),
        ("Non-users (\"No\")", int((df["used_digital_health"] == "No").sum()), "excluded from analytic sample"),
        ("Usage question blank", int((df["used_digital_health"] == "(blank)").sum()), "excluded: eligibility unknown"),
        ("Primary analytic sample A (users)", len(users), ""),
        ("  of which straight-liners", int((X.nunique(axis=1) == 1).sum()), "retained; tested in S2"),
        ("  of which exact duplicate item patterns", int(X.duplicated(keep="first").sum()), "retained; tested in S3"),
    ]
    return pd.DataFrame(rows, columns=["Stage", "Count", "Treatment"])


# ------------------------------------------------------------------ measurement
def cronbach(items: pd.DataFrame) -> float:
    k = items.shape[1]
    return float(k / (k - 1) * (1 - items.var(ddof=1).sum() / items.sum(axis=1).var(ddof=1)))


def reliability(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for code, (name, its, h) in CONSTRUCTS.items():
        r = d[its[0]].corr(d[its[1]])
        rows.append({"Construct": name, "Code": code, "Items": " + ".join(its), "Inter-item r": r,
                     "Spearman-Brown": 2 * r / (1 + r), "Cronbach α": cronbach(d[its])})
    return pd.DataFrame(rows)


def composites(d: pd.DataFrame) -> pd.DataFrame:
    c = pd.DataFrame({k: d[v[1]].mean(axis=1) for k, v in CONSTRUCTS.items()})
    c["TBCI"] = d[OUTCOME]
    c["IMP"] = d[IMPORTANCE]
    return c


def kmo_bartlett(X: pd.DataFrame) -> dict:
    R = np.corrcoef(X.values, rowvar=False)
    n, p = X.shape
    inv = np.linalg.inv(R)
    d = np.sqrt(np.outer(np.diag(inv), np.diag(inv)))
    P = -inv / d
    np.fill_diagonal(P, 0)
    R0 = R.copy()
    np.fill_diagonal(R0, 0)
    kmo = (R0 ** 2).sum() / ((R0 ** 2).sum() + (P ** 2).sum())
    chi = -(n - 1 - (2 * p + 5) / 6) * np.log(np.linalg.det(R))
    dof = p * (p - 1) / 2
    return {"KMO": float(kmo), "Bartlett chi2": float(chi), "df": int(dof), "p": float(stats.chi2.sf(chi, dof))}


def parallel_analysis(X: pd.DataFrame, n_iter: int = 1000, seed: int = 1) -> pd.DataFrame:
    n, p = X.shape
    ev = np.sort(np.linalg.eigvalsh(np.corrcoef(X.values, rowvar=False)))[::-1]
    rng = np.random.default_rng(seed)
    sims = np.empty((n_iter, p))
    for i in range(n_iter):
        Z = rng.standard_normal((n, p))
        sims[i] = np.sort(np.linalg.eigvalsh(np.corrcoef(Z, rowvar=False)))[::-1]
    thr = np.percentile(sims, 95, axis=0)
    return pd.DataFrame({"Component": range(1, p + 1), "Eigenvalue": ev, "Random 95th pct": thr,
                         "Retain": ev > thr, "Variance share": ev / p})


def htmt(d: pd.DataFrame) -> pd.DataFrame:
    R = d[[q for c in CONSTRUCTS.values() for q in c[1]]].corr()
    codes = list(CONSTRUCTS)
    out = pd.DataFrame(np.nan, index=codes, columns=codes)
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            ia, ib = CONSTRUCTS[a][1], CONSTRUCTS[b][1]
            hetero = np.mean([R.loc[x, y] for x in ia for y in ib])
            mono_a, mono_b = R.loc[ia[0], ia[1]], R.loc[ib[0], ib[1]]
            out.loc[a, b] = out.loc[b, a] = hetero / np.sqrt(mono_a * mono_b)
    return out


# ------------------------------------------------------------------ associations
def spearman_ci(x, y, n_boot=5000, seed=7):
    x, y = np.asarray(x), np.asarray(y)
    rho, p2 = stats.spearmanr(x, y)
    rng = np.random.default_rng(seed)
    n = len(x)
    bs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        bs[i] = stats.spearmanr(x[idx], y[idx])[0]
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    p1 = p2 / 2 if rho > 0 else 1 - p2 / 2  # one-sided, positive direction pre-specified
    return float(rho), float(lo), float(hi), float(p1)


def hypothesis_tests(c: pd.DataFrame, n_boot=5000) -> pd.DataFrame:
    rows = []
    for k, (name, its, h) in CONSTRUCTS.items():
        rho, lo, hi, p1 = spearman_ci(c[k], c["TBCI"], n_boot=n_boot)
        rows.append({"H": h, "Construct": name, "Code": k, "Spearman ρ": rho, "CI low": lo, "CI high": hi,
                     "p (one-sided)": p1})
    t = pd.DataFrame(rows)
    t["p (Holm)"] = multipletests(t["p (one-sided)"], method="holm")[1]
    t["Decision"] = np.where((t["Spearman ρ"] > 0) & (t["p (Holm)"] < 0.05),
                             "Supported (association with TBCI proxy)", "Not supported")
    return t


@dataclass
class OLSResult:
    n: int
    r2: float
    adj_r2: float
    f_p: float
    table: pd.DataFrame = field(repr=False)


def ols_unique(c: pd.DataFrame, n_boot=5000, seed=11) -> OLSResult:
    d = c[DRIVERS + ["TBCI"]].dropna()
    X = sm.add_constant(d[DRIVERS])
    m = sm.OLS(d["TBCI"], X).fit(cov_type="HC3")
    z = (d - d.mean()) / d.std(ddof=1)
    beta = sm.OLS(z["TBCI"], sm.add_constant(z[DRIVERS])).fit().params[DRIVERS]
    rng = np.random.default_rng(seed)
    n = len(d)
    bs = np.empty((n_boot, len(DRIVERS)))
    arr = d.values
    for i in range(n_boot):
        s = arr[rng.integers(0, n, n)]
        s = (s - s.mean(0)) / s.std(0, ddof=1)
        A = np.column_stack([np.ones(n), s[:, :4]])
        bs[i] = np.linalg.lstsq(A, s[:, 4], rcond=None)[0][1:]
    lo, hi = np.nanpercentile(bs, [2.5, 97.5], axis=0)
    vif = [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])]
    tbl = pd.DataFrame({"Code": DRIVERS, "Predictor": [CONSTRUCTS[k][0] for k in DRIVERS],
                        "B": m.params[DRIVERS].values, "Robust SE (HC3)": m.bse[DRIVERS].values,
                        "p": m.pvalues[DRIVERS].values, "β (std.)": beta.values,
                        "β CI low": lo, "β CI high": hi, "VIF": vif})
    return OLSResult(int(m.nobs), float(m.rsquared), float(m.rsquared_adj), float(m.f_pvalue), tbl)


def ordinal_robustness(c: pd.DataFrame) -> pd.DataFrame:
    d = c[DRIVERS + ["TBCI"]].dropna()
    y = pd.Categorical(d["TBCI"].astype(int), ordered=True)
    m = OrderedModel(y, d[DRIVERS], distr="logit").fit(method="bfgs", disp=False, maxiter=2000)
    return pd.DataFrame({"Code": DRIVERS, "Log-odds": m.params[DRIVERS].values,
                         "Odds ratio": np.exp(m.params[DRIVERS].values), "p": m.pvalues[DRIVERS].values})


def users_vs_nonusers(df: pd.DataFrame) -> pd.DataFrame:
    c = composites(df)
    u = df["used_digital_health"] == "Yes"
    nu = df["used_digital_health"] == "No"
    rows = []
    for k in DRIVERS + ["TBCI", "IMP"]:
        a, b = c.loc[u, k], c.loc[nu, k]
        U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        rb = 1 - 2 * U / (len(a) * len(b))
        rows.append({"Measure": k, "Users mean": a.mean(), "Non-users mean": b.mean(),
                     "Mann-Whitney U": U, "p": p, "Rank-biserial": -rb})
    return pd.DataFrame(rows)


def _min_f2(u: int, v: int, alpha=0.05, target=0.80) -> float:
    """Smallest Cohen's f² detectable with numerator df u, denominator df v (noncentral F, λ = f²(u+v+1))."""
    crit = stats.f.ppf(1 - alpha, u, v)
    lo, hi = 0.0, 5.0
    for _ in range(80):
        mid = (lo + hi) / 2
        pw = stats.ncf.sf(crit, u, v, mid * (u + v + 1))
        lo, hi = (mid, hi) if pw < target else (lo, mid)
    return hi


def power(n: int) -> dict:
    f2_model = _min_f2(4, n - 5)
    f2_one = _min_f2(1, n - 5)
    return {"n": n, "min f2 (4-predictor model)": f2_model, "min R2 equivalent": f2_model / (1 + f2_model),
            "min f2 (single predictor, unique)": f2_one}


def item_descriptives(d: pd.DataFrame) -> pd.DataFrame:
    X = d[list(ITEMS)]
    rows = []
    for q in ITEMS:
        s = X[q]
        rows.append({"Item": q, "Statement": ITEMS[q], "Mean": s.mean(), "SD": s.std(ddof=1),
                     "% Agree (4–5)": 100 * (s >= 4).mean(), "% Neutral": 100 * (s == 3).mean(),
                     "% Disagree (1–2)": 100 * (s <= 2).mean(),
                     "Export format": "numeric 1–5" if q in NUMERIC_EXPORT else "text"})
    return pd.DataFrame(rows)


DECK_REPORTED = {"α (Q14, Q15)": 0.755, "r (Q10, Q12)": 0.69, "r (Q14, Q15)": 0.61,
                 "R² (Q15 ~ Q10 + Q12)": 0.207, "B (Q14 ~ Q15)": 0.596}


def deck_reproduction(df: pd.DataFrame) -> pd.DataFrame:
    """Recompute the statistics shown in the team's final deck from all 112 rows, using only the four
    items Google Forms exported as numbers (Q10, Q12, Q14, Q15) — the subset the deck appears to have used."""
    import statsmodels.api as sm
    d = df[NUMERIC_EXPORT].astype(float)
    r2 = sm.OLS(d["Q15"], sm.add_constant(d[["Q10", "Q12"]])).fit().rsquared
    b = sm.OLS(d["Q14"], sm.add_constant(d[["Q15"]])).fit().params["Q15"]
    ours = {"α (Q14, Q15)": cronbach(d[["Q14", "Q15"]]), "r (Q10, Q12)": d["Q10"].corr(d["Q12"]),
            "r (Q14, Q15)": d["Q14"].corr(d["Q15"]), "R² (Q15 ~ Q10 + Q12)": r2, "B (Q14 ~ Q15)": b}
    return pd.DataFrame([{"Statistic": k, "Reported in deck": v, "Recomputed (n = %d)" % len(d): ours[k],
                          "Difference": ours[k] - v} for k, v in DECK_REPORTED.items()])


def run_all(df: pd.DataFrame | None = None, n_boot: int = 5000) -> dict:
    df = load() if df is None else df
    S = samples(df)
    A = S["A"]
    cA = composites(A)
    X10 = A[list(ITEMS)]
    pa = parallel_analysis(X10)
    res = {
        "flow": flow(df),
        "n": {k: len(v) for k, v in S.items()},
        "profile": {col: A[col].value_counts() for col in ["gender", "age_band", "profession"]},
        "profile_all": {col: pd.crosstab(df[col], df["used_digital_health"]) for col in ["gender", "age_band", "profession"]},
        "dates": df["response_date"].value_counts().sort_index(),
        "items": item_descriptives(A),
        "reliability": reliability(A),
        "kmo": kmo_bartlett(X10),
        "parallel": pa,
        "harman_share": float(pa["Variance share"].iloc[0]),
        "htmt": htmt(A),
        "corr": cA[DRIVERS + ["TBCI", "IMP"]].corr(method="spearman"),
        "hyp": hypothesis_tests(cA, n_boot=n_boot),
        "ols": ols_unique(cA, n_boot=n_boot),
        "ordinal": ordinal_robustness(cA),
        "q14_q15": spearman_ci(A[OUTCOME], A[IMPORTANCE], n_boot=n_boot)[:3],
        "groups": users_vs_nonusers(df),
        "power": power(len(A)),
        "sensitivity": {},
        "deck": deck_reproduction(df),
    }
    for key in ["S1", "S2", "S3"]:
        c = composites(S[key])
        res["sensitivity"][key] = {"n": len(S[key]), "hyp": hypothesis_tests(c, n_boot=2000),
                                   "ols": ols_unique(c, n_boot=2000)}
    return res
