import numpy as np
import pandas as pd
import pytest

from core import dpdp, kano, locker, pipeline, quality, roi, sample_data
from core import stats as S


@pytest.fixture(scope="module")
def analysis():
    return pipeline.run(sample_data.synthetic_survey(), n_boot=300)


def test_alpha_known_value():
    items = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, 2, 3, 4, 5]})
    assert S.cronbach_alpha(items) == pytest.approx(1.0)


def test_synthetic_passes_audit_and_cleaning(analysis):
    assert analysis.verdict.startswith("FIT")
    assert analysis.flow["Remaining"].is_monotonic_decreasing
    assert len(analysis.clean) >= 180


def test_reliability_mostly_acceptable(analysis):
    rel = analysis.reliability.set_index("Code")["Cronbach α"]
    for code in ["TRU", "TRN", "CON", "GOV", "COM", "USE"]:
        assert rel[code] >= 0.70


def test_trust_predicts_usage(analysis):
    t = analysis.usage_model.table.iloc[0]
    assert t["β (std.)"] > 0.3 and t["p"] < 0.001


def test_random_data_fails_audit():
    rng = np.random.default_rng(1)
    df = pd.DataFrame(rng.integers(1, 6, (220, 30)), columns=[f"Q{i}" for i in range(30)])
    _, verdict = quality.audit(df, list(df.columns))
    assert verdict.startswith("NOT FIT")


def test_minors_and_nonusers_removed(analysis):
    age_col = pipeline.find_col(analysis.clean.columns, "age range")
    assert "Under 18" not in set(analysis.clean[age_col])


def test_policy_engine_and_ledger():
    L = locker.Locker()
    L.give_initial_consent({"lab": True, "pharmacy": False}, "en")
    assert L.request_access("lab", "lab_report").allowed
    assert not L.request_access("pharmacy", "prescription").allowed
    assert not L.request_access("lab", "lab_report", purpose="marketing").allowed
    assert not L.request_access("lab", "history").allowed
    L.set_consent("pharmacy", True)
    assert L.request_access("pharmacy", "prescription").allowed
    assert L.verify_chain() == (True, None)
    L.tamper(2)
    ok, bad = L.verify_chain()
    assert not ok and bad == 2


def test_doctor_consent_cannot_be_revoked():
    L = locker.Locker()
    L.give_initial_consent({}, "en")
    with pytest.raises(ValueError):
        L.set_consent("doctor", False)


def test_grievance_has_case_id_and_sla():
    L = locker.Locker()
    cid = L.raise_grievance(locker.GRIEVANCE_CATEGORIES[0], "x")
    g = L.grievances()[0]
    assert g["case_id"] == cid and cid.startswith("ZG-")
    assert g["resolve_due"] > g["ack_due"]


def test_phi_checker():
    assert "hba1c" in locker.phi_check("Your HbA1c result is high")
    assert locker.phi_check(locker.safe_rewrite("x")) == []


def test_kano_table():
    assert kano.classify_pair("Like", "Dislike") == "O"
    assert kano.classify_pair("Expect", "Dislike") == "M"
    assert kano.classify_pair("Like", "Neutral") == "A"
    res = kano.analyse(sample_data.demo_kano())
    assert set(res["Category"]) <= set(kano.NAMES.values())


def test_roi_monotonic_in_uplift():
    a = roi.Assumptions()
    from dataclasses import replace
    assert roi.npv(replace(a, repeat_uplift_pp=0.05)) > roi.npv(a)
    assert roi.breakeven_uplift(a) is not None


def test_dpdp_locker_improves_score():
    lv = {c[0]: 1 for c in dpdp.CONTROLS}
    assert dpdp.overall(dpdp.score(lv, True)) > dpdp.overall(dpdp.score(lv))
