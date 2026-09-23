"""Survey data-quality audit.

Run this BEFORE any reliability / regression work. It answers one question:
"Do these responses contain real, structured opinions — or could they be
random / auto-filled?" A dataset that fails here should not be used to make
inferential claims, however good the downstream numbers look.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats as sps


@dataclass
class Check:
    name: str
    value: str
    status: str   # "pass" | "warn" | "fail"
    meaning: str


def bartlett_sphericity(X: pd.DataFrame) -> tuple[float, float, float]:
    X = X.dropna()
    n, p = X.shape
    R = np.corrcoef(X.values, rowvar=False)
    sign, logdet = np.linalg.slogdet(R)
    chi = -(n - 1 - (2 * p + 5) / 6) * logdet
    dof = p * (p - 1) / 2
    return float(chi), float(dof), float(sps.chi2.sf(chi, dof))


def kmo(X: pd.DataFrame) -> float:
    R = np.corrcoef(X.dropna().values, rowvar=False)
    inv = np.linalg.pinv(R)
    d = np.sqrt(np.outer(np.diag(inv), np.diag(inv)))
    P = -inv / d
    np.fill_diagonal(P, 0)
    R0 = R.copy()
    np.fill_diagonal(R0, 0)
    return float((R0 ** 2).sum() / ((R0 ** 2).sum() + (P ** 2).sum()))


def permutation_null(X: pd.DataFrame, n_perm: int = 200, seed: int = 0) -> tuple[float, float, float]:
    """Compare mean |r| between items with the same data shuffled column-by-column.

    Shuffling keeps every item's answer distribution but destroys any link
    between items — i.e. it simulates 'everyone answered each question at random'.
    Returns (observed, null_mean, share_of_null >= observed).
    """
    X = X.dropna().values
    p = X.shape[1]
    iu = np.triu_indices(p, 1)
    obs = np.abs(np.corrcoef(X, rowvar=False)[iu]).mean()
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        Y = np.column_stack([rng.permutation(X[:, j]) for j in range(p)])
        null[i] = np.abs(np.corrcoef(Y, rowvar=False)[iu]).mean()
    return float(obs), float(null.mean()), float((null >= obs).mean())


def audit(df: pd.DataFrame, items: list[str], timestamp_col: str | None = None,
          age_col: str | None = None, usage_col: str | None = None,
          minor_labels: tuple[str, ...] = ("Under 18",),
          nonuser_labels: tuple[str, ...] = ("Never",)) -> tuple[list[Check], str]:
    X = df[items].apply(pd.to_numeric, errors="coerce")
    checks: list[Check] = []

    chi, dof, p = bartlett_sphericity(X)
    checks.append(Check("Bartlett's test of sphericity", f"χ²={chi:.0f}, df={dof:.0f}, p={p:.3g}",
                        "pass" if p < 0.001 else "fail",
                        "Tests whether items are related at all. p ≥ 0.05 means the data is "
                        "consistent with every item being answered independently."))
    k = kmo(X)
    checks.append(Check("Kaiser-Meyer-Olkin (KMO)", f"{k:.2f}",
                        "pass" if k >= 0.7 else ("warn" if k >= 0.5 else "fail"),
                        "Sampling adequacy for factor structure. < 0.5 is unacceptable."))
    obs, null, share = permutation_null(X)
    checks.append(Check("Mean |r| vs. shuffled-random data", f"{obs:.3f} vs {null:.3f} (random ≥ real in {share:.0%} of shuffles)",
                        "pass" if share < 0.01 else "fail",
                        "Real opinions create correlations far above shuffled data. "
                        "If shuffled data looks the same, the structure is indistinguishable from noise."))
    straight = int((X.nunique(axis=1) == 1).sum())
    checks.append(Check("Straight-lining (same answer to every item)", f"{straight} of {len(X)}",
                        "pass" if straight / len(X) < 0.05 else "warn",
                        "Respondents who clicked the same option throughout."))
    dup = int(X.duplicated().sum())
    checks.append(Check("Duplicate response patterns", str(dup), "pass" if dup == 0 else "warn",
                        "Identical rows suggest copy-paste or bot submissions."))
    miss = float(X.isna().mean().mean())
    checks.append(Check("Missing values", f"{miss:.1%}", "pass" if miss < 0.05 else "warn",
                        "Share of blank Likert cells."))

    if timestamp_col and timestamp_col in df:
        ts = pd.to_datetime(df[timestamp_col], errors="coerce").dropna()
        daily = ts.dt.date.value_counts()
        full_days = daily.iloc[1:-1] if len(daily) > 2 else daily
        cv = float(full_days.std() / full_days.mean()) if len(full_days) > 1 and full_days.mean() else float("nan")
        checks.append(Check("Submission cadence (daily count variation)",
                            f"{len(daily)} days, CV={cv:.2f}, typical/day={int(full_days.median())}",
                            "warn" if cv < 0.1 else "pass",
                            "Organic surveys arrive in bursts after each share. A near-constant daily "
                            "count (CV < 0.1) suggests scheduled or quota-filled entry."))
    if age_col and age_col in df:
        minors = int(df[age_col].isin(minor_labels).sum())
        checks.append(Check("Respondents under 18", str(minors), "pass" if minors == 0 else "fail",
                            "Collecting minors' data needs verifiable parental consent (DPDP s.9) and "
                            "usually ethics approval. Exclude these rows."))
    if usage_col and usage_col in df:
        nonusers = int(df[usage_col].isin(nonuser_labels).sum())
        checks.append(Check("Non-users rating platforms", str(nonusers), "pass" if nonusers == 0 else "warn",
                            "People who never use digital health cannot evaluate platform experience. "
                            "Screen them out or analyse separately."))

    fails = sum(c.status == "fail" for c in checks[:3])
    if fails >= 2:
        verdict = ("NOT FIT FOR INFERENCE — the response structure is statistically indistinguishable "
                   "from random answering. Do not report reliability, correlation or regression results "
                   "from this data as findings.")
    elif any(c.status == "fail" for c in checks):
        verdict = "USE WITH CAUTION — fix the failed checks (exclude rows, re-screen) before analysis."
    else:
        verdict = "FIT FOR ANALYSIS — proceed to reliability and hypothesis testing."
    return checks, verdict


# ---------------------------------------------------------------- cleaning
def clean_form(df: pd.DataFrame, items: list[str], *, consent_col: str | None = None,
               age_col: str | None = None, services_col: str | None = None,
               attention_col: str | None = None, attention_answer: str = "Agree",
               minor_labels: tuple[str, ...] = ("Under 18",),
               max_missing: float = 0.10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply documented exclusion rules in order; return (clean_df, flow_table).

    The flow table is the survey equivalent of a CONSORT diagram: it shows how
    many rows each rule removed, so the analysis is transparent and repeatable.
    """
    flow = [("Raw responses", len(df), "")]
    cur = df.copy()

    def step(mask, label, why):
        nonlocal cur
        before = len(cur)
        cur = cur[~mask.reindex(cur.index, fill_value=False)]
        flow.append((label, len(cur), f"−{before - len(cur)}  ({why})"))

    if consent_col and consent_col in cur:
        step(cur[consent_col].fillna("No").ne("Yes"), "Gave informed consent", "declined or blank consent")
    if age_col and age_col in cur:
        step(cur[age_col].isin(minor_labels), "Aged 18+", "minors excluded (DPDP s.9 / research ethics)")
    if services_col and services_col in cur:
        step(cur[services_col].fillna("").str.contains("None of the above"), "Past-year users only",
             "non-users cannot rate platform experience")
    if attention_col and attention_col in cur:
        step(cur[attention_col].ne(attention_answer), "Passed attention check", "failed instructed-response item")
    num = cur[items].apply(pd.to_numeric, errors="coerce")
    step(num.nunique(axis=1).eq(1) & num.notna().all(axis=1), "No straight-lining",
         "identical answer to every rating item")
    num = cur[items].apply(pd.to_numeric, errors="coerce")
    step(num.isna().mean(axis=1) > max_missing, f"≤{max_missing:.0%} items missing", "too many blanks")
    table = pd.DataFrame(flow, columns=["Stage", "Remaining", "Removed (reason)"])
    return cur, table
