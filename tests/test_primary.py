"""Integrity tests for the genuine primary survey and its published results."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core import primary as P

ROOT = Path(__file__).resolve().parents[1]
ITEMS = [f"Q{i}" for i in range(6, 16)]


@pytest.fixture(scope="module")
def df():
    return P.load()


def test_deidentified_file_has_no_direct_identifiers(df):
    raw = pd.read_csv(P.DEID_PATH)
    lowered = [c.lower() for c in raw.columns]
    assert not any(k in c for c in lowered for k in ("name", "email", "phone", "timestamp"))
    assert raw["response_id"].is_unique and raw["response_id"].str.match(r"^R\d{3}$").all()
    # dates only, no time of day
    assert raw["response_date"].astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").all()


def test_counts(df):
    assert len(df) == 112
    s = P.samples(df)
    assert len(s["A"]) == 74
    used = df["used_digital_health"].fillna("(blank)")
    assert (used == "No").sum() == 37
    assert (~used.isin(["Yes", "No"])).sum() == 1


def test_items_coded_1_to_5_and_positively_related(df):
    X = df[ITEMS]
    assert X.notna().all().all()
    assert X.isin([1, 2, 3, 4, 5]).all().all()
    r = X.corr(method="spearman").to_numpy()
    assert (r[np.triu_indices(len(ITEMS), 1)] > 0).all()  # no item is reverse-scored by mistake


def test_published_results_match_recomputation(df):
    pub = json.loads((ROOT / "outputs" / "primary" / "results.json").read_text())
    R = P.run_all(df, n_boot=200)
    assert pub["n"] == R["n"]
    for h, row in R["hyp"].set_index("H").iterrows():
        assert abs(pub["hyp"][h]["Spearman ρ"] - row["Spearman ρ"]) < 1e-3
        assert pub["hyp"][h]["Decision"] == row["Decision"]
    assert abs(pub["ols"]["r2"] - R["ols"].r2) < 1e-3
    for code, row in R["ols"].table.set_index("Code").iterrows():
        assert abs(pub["ols"]["table"][code]["β (std.)"] - row["β (std.)"]) < 1e-3
    assert abs(pub["kmo"]["KMO"] - R["kmo"]["KMO"]) < 1e-6


def test_h5_and_mediation_not_claimed():
    text = (ROOT / "docs" / "primary" / "RESULTS_PRIMARY.md").read_text()
    assert "H5 and mediation\nNot tested" in text
    hyp = pd.read_csv(ROOT / "outputs" / "primary" / "hypotheses.csv")
    assert set(hyp["H"]) == {"H1", "H2", "H3", "H4"}


def test_raw_file_not_in_repo():
    hits = [p for p in ROOT.rglob("*.xlsx") if "primary" in p.name.lower() and ".git" not in p.parts]
    assert not hits, hits
    assert not list((ROOT / "data" / "primary").glob("*raw*"))
