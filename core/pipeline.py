"""End-to-end analysis pipeline: raw Google-Forms export → findings.

detect columns → recode Likert → clean (documented exclusions) → quality audit
→ reliability → composites → correlations → regressions (+VIF) → mediation
→ hypothesis table. Used by the Research Lab page and by scripts/run_analysis.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import quality
from . import stats as S


def find_col(columns, *needles: str) -> str | None:
    for c in columns:
        low = str(c).lower()
        if all(n in low for n in needles):
            return c
    return None


@dataclass
class Analysis:
    raw_n: int
    clean: pd.DataFrame
    flow: pd.DataFrame
    mapping: dict[str, list[str]]
    checks: list
    verdict: str
    reliability: pd.DataFrame
    comp: pd.DataFrame
    r: pd.DataFrame
    p: pd.DataFrame
    trust_model: S.RegResult
    usage_model: S.RegResult
    full_model: S.RegResult
    hypotheses: pd.DataFrame
    mediations: list = field(default_factory=list)
    profile: dict = field(default_factory=dict)


def run(raw: pd.DataFrame, mapping: dict[str, list[str]] | None = None, n_boot: int = 2000,
        drivers: list[str] | None = None) -> Analysis:
    cols = list(raw.columns)
    mapping = mapping or S.detect_form_constructs(cols) or S.detect_constructs(cols)
    mapping = {k: v for k, v in mapping.items() if v}
    items = [c for v in mapping.values() for c in v]

    att = find_col(cols, "reading carefully")
    extra = [att] if att else []
    rec = S.coerce_likert(raw[items + extra]) if items else raw
    df = raw.copy()
    df[items] = rec[items]

    clean, flow = quality.clean_form(
        df, items,
        consent_col=find_col(cols, "agree to take part"),
        age_col=find_col(cols, "age range"),
        services_col=find_col(cols, "services have you used"),
        attention_col=att, attention_answer="Agree")
    checks, verdict = quality.audit(clean, items, timestamp_col=find_col(cols, "timestamp"),
                                    age_col=find_col(cols, "age range"),
                                    usage_col=find_col(cols, "how often"))

    rel = S.reliability_table(clean, mapping)
    comp = S.composites(clean, mapping)
    r, p = S.correlation_matrix(comp)

    drivers = drivers or [d for d in ["TRN", "CON", "GOV", "COM", "PRV", "CRD", "REL", "BDM"] if d in comp]
    trust_model = S.regress(comp, "TRU", drivers)
    usage_model = S.regress(comp, "USE", ["TRU"])
    full_extra = [c for c in ["REL", "BUS"] if c in comp]
    full_model = S.regress(comp, "USE", ["TRU"] + full_extra)
    hyp = S.hypothesis_table(trust_model, usage_model)

    meds = [S.mediation(comp, x, "TRU", "USE", n_boot=n_boot) for x in drivers if x in ("TRN", "CON", "GOV", "COM")]

    profile = {}
    for label, needles in [("Age", ("age range",)), ("Location", ("where do you live",)),
                           ("Preferred language", ("language do you prefer",)),
                           ("Platform", ("platform do you use most",)), ("Usage frequency", ("how often",))]:
        c = find_col(cols, *needles)
        if c is not None:
            profile[label] = clean[c].value_counts()

    return Analysis(len(raw), clean, flow, mapping, checks, verdict, rel, comp, r, p,
                    trust_model, usage_model, full_model, hyp, meds, profile)
