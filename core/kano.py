"""Kano model classification (Kano et al., 1984) with Berger et al. (1993) CS coefficients."""
from __future__ import annotations

import pandas as pd

ANSWERS = ["Like", "Expect", "Neutral", "Live with", "Dislike"]
NAMES = {"A": "Attractive", "O": "One-dimensional (Performance)", "M": "Must-be",
         "I": "Indifferent", "R": "Reverse", "Q": "Questionable"}

# rows = functional answer, columns = dysfunctional answer
_TABLE = {
    "Like":      ["Q", "A", "A", "A", "O"],
    "Expect":    ["R", "I", "I", "I", "M"],
    "Neutral":   ["R", "I", "I", "I", "M"],
    "Live with": ["R", "I", "I", "I", "M"],
    "Dislike":   ["R", "R", "R", "R", "Q"],
}

_ALIASES = {
    "i like it": "Like", "like": "Like", "i expect it": "Expect", "must-be": "Expect",
    "expect": "Expect", "i am neutral": "Neutral", "neutral": "Neutral",
    "i can live with it": "Live with", "live with": "Live with", "i can tolerate it": "Live with",
    "i dislike it": "Dislike", "dislike": "Dislike",
}


def normalise(ans: str) -> str | None:
    if not isinstance(ans, str):
        return None
    a = ans.strip()
    if a in ANSWERS:
        return a
    return _ALIASES.get(a.lower())


def classify_pair(functional: str, dysfunctional: str) -> str | None:
    f, d = normalise(functional), normalise(dysfunctional)
    if f is None or d is None:
        return None
    return _TABLE[f][ANSWERS.index(d)]


def analyse(long_df: pd.DataFrame) -> pd.DataFrame:
    """long_df columns: feature, functional, dysfunctional (one row per respondent × feature)."""
    df = long_df.copy()
    df["cat"] = [classify_pair(f, d) for f, d in zip(df["functional"], df["dysfunctional"])]
    df = df.dropna(subset=["cat"])
    counts = df.pivot_table(index="feature", columns="cat", aggfunc="size", fill_value=0)
    for c in "AOMIRQ":
        if c not in counts:
            counts[c] = 0
    counts = counts[list("AOMIRQ")]
    total = counts.sum(axis=1)
    core = counts[["A", "O", "M", "I"]].sum(axis=1).replace(0, 1)
    out = counts.copy()
    out["n"] = total
    out["Category"] = counts[list("AOMI")].idxmax(axis=1).map(NAMES)
    out["Better (satisfaction)"] = ((counts["A"] + counts["O"]) / core).round(3)
    out["Worse (dissatisfaction)"] = (-(counts["O"] + counts["M"]) / core).round(3)
    rank = {"Must-be": 1, "One-dimensional (Performance)": 2, "Attractive": 3, "Indifferent": 4,
            "Reverse": 5, "Questionable": 6}
    out["Priority"] = out["Category"].map(rank)
    out = out.sort_values(["Priority", "Worse (dissatisfaction)"])
    return out.reset_index()


def mvp_recommendation(result: pd.DataFrame) -> dict[str, list[str]]:
    groups = {"Pilot MVP (must ship)": [], "Scale phase (competitive)": [],
              "Delighters (differentiate)": [], "Deprioritise": []}
    for _, r in result.iterrows():
        c = r["Category"]
        if c == "Must-be":
            groups["Pilot MVP (must ship)"].append(r["feature"])
        elif c.startswith("One-dimensional"):
            groups["Scale phase (competitive)"].append(r["feature"])
        elif c == "Attractive":
            groups["Delighters (differentiate)"].append(r["feature"])
        else:
            groups["Deprioritise"].append(r["feature"])
    return groups
