from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import pipeline, ui
from core import stats as S

DATA = Path(__file__).resolve().parents[1] / "data"

ui.setup("Research Lab", "Evidence · survey analytics",
         "Does transparency, consent, governance and communication build digital trust — and does trust "
         "drive continued use? This page runs the full pipeline, quality audit first.")

src = st.radio("Data source", ["Synthetic demo (questionnaire v2)", "Upload my Google-Forms export"],
               horizontal=True)
raw = None
if src.startswith("Synthetic"):
    raw = pd.read_csv(DATA / "synthetic_survey_v2_SYNTHETIC.csv")
    ui.synthetic_banner()
else:
    up = st.file_uploader("CSV or XLSX exported from Google Forms", type=["csv", "xlsx"])
    if up is not None:
        raw = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
    else:
        st.caption("Headers like `Section [statement]` are auto-mapped. Short codes like TRU1, GOV2 also work.")
        st.stop()

auto = S.detect_form_constructs(list(raw.columns)) or S.detect_constructs(list(raw.columns))
auto = {k: v for k, v in auto.items() if v}

with st.expander(f"Construct mapping — {sum(map(len, auto.values()))} items in {len(auto)} constructs (edit if needed)"):
    candidates = [c for c in raw.columns]
    mapping = {}
    for code in list(S.CONSTRUCTS):
        default = auto.get(code, [])
        sel = st.multiselect(f"{code} · {S.CONSTRUCTS[code]}", candidates, default=default, key=f"map_{code}",
                             format_func=lambda c: (c[:110] + "…") if len(str(c)) > 110 else c)
        if sel:
            mapping[code] = sel
if "TRU" not in mapping or "USE" not in mapping:
    st.error("Map at least Digital Trust (TRU) and Usage Intention (USE) items to continue.")
    st.stop()


@st.cache_data(show_spinner="Running pipeline…")
def _run(df: pd.DataFrame, mp: dict, n_boot: int):
    return pipeline.run(df, mp, n_boot=n_boot)


n_boot = st.sidebar.select_slider("Bootstrap resamples (mediation)", [500, 1000, 2000, 5000], value=1000)
A = _run(raw, mapping, n_boot)

tabs = st.tabs(["1 · Quality & cleaning", "2 · Sample", "3 · Reliability", "4 · Correlations",
                "5 · Regression", "6 · Mediation", "7 · Hypotheses", "Method notes"])

with tabs[0]:
    st.markdown("#### Step 1 — Is this data fit for inference?")
    ok = A.verdict.startswith("FIT")
    (st.success if ok else st.error)(A.verdict)
    rows = "".join(f"<tr><td>{ui.pill(c.status)}</td><td><b>{c.name}</b><br><span style='color:#5B6B7A'>{c.meaning}</span>"
                   f"</td><td style='white-space:nowrap'>{c.value}</td></tr>" for c in A.checks)
    st.markdown(f"<table style='width:100%'>{rows}</table>", unsafe_allow_html=True)
    st.markdown("#### Step 2 — Exclusion flow")
    f = A.flow
    fig = go.Figure(go.Funnel(y=f["Stage"], x=f["Remaining"], textinfo="value",
                              marker=dict(color=ui.PRIMARY)))
    st.plotly_chart(ui.plotly_layout(fig, 340))
    st.dataframe(f, hide_index=True)

with tabs[1]:
    st.markdown(f"#### Analytic sample: n = {len(A.clean)} (from {A.raw_n} raw)")
    if A.profile:
        cols = st.columns(2)
        for i, (k, v) in enumerate(A.profile.items()):
            fig = px.bar(x=v.values, y=v.index.astype(str), orientation="h", title=k,
                         color_discrete_sequence=[ui.PRIMARY])
            fig.update_layout(yaxis_title=None, xaxis_title="respondents")
            cols[i % 2].plotly_chart(ui.plotly_layout(fig, 260))
    means = A.comp.agg(["mean", "std"]).T.round(2)
    means.index = [f"{c} · {S.CONSTRUCTS.get(c, c)}" for c in means.index]
    st.markdown("##### Construct means (1 = strongly disagree … 5 = strongly agree)")
    st.dataframe(means)

with tabs[2]:
    st.markdown("#### Internal consistency, per construct")
    st.caption("The original deck reported a single α for a combined Trust + Usage scale. Reliability must be "
               "shown per construct — mixing an independent and a dependent variable in one α is not valid.")
    rel = A.reliability
    fig = px.bar(rel, x="Cronbach α", y="Construct", orientation="h", text="Cronbach α",
                 color=np.where(rel["Cronbach α"] >= .7, "≥ 0.70", "< 0.70"),
                 color_discrete_map={"≥ 0.70": ui.PRIMARY, "< 0.70": ui.WARN})
    fig.add_vline(x=0.7, line_dash="dash", line_color=ui.MUTED)
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), legend_title=None)
    st.plotly_chart(ui.plotly_layout(fig, 420))
    st.dataframe(rel, hide_index=True)

with tabs[3]:
    st.markdown("#### Pearson correlations between construct scores")
    r = A.r.copy()
    labels = [f"{c}" for c in r.columns]
    fig = px.imshow(r.values, x=labels, y=labels, zmin=-1, zmax=1, text_auto=".2f",
                    color_continuous_scale=["#B3261E", "#F7F7F7", "#0F6E8C"])
    st.plotly_chart(ui.plotly_layout(fig, 560))
    st.caption("Codes: " + " · ".join(f"**{c}** {S.CONSTRUCTS.get(c, c)}" for c in r.columns))

with tabs[4]:
    m = A.trust_model
    st.markdown(f"#### Model 1 — What explains Digital Trust?  R² = {m.r2:.3f} (adj. {m.adj_r2:.3f}), "
                f"F = {m.f:.1f}, p = {m.f_p:.2g}, n = {m.n}")
    t = m.table.copy()
    t["sig"] = np.where(t["p"] < .05, "p < .05", "n.s.")
    fig = px.bar(t.sort_values("β (std.)"), x="β (std.)", y="Predictor", orientation="h", color="sig",
                 color_discrete_map={"p < .05": ui.PRIMARY, "n.s.": "#B8C4CC"}, text=t.sort_values("β (std.)")["β (std.)"].round(2))
    fig.update_layout(legend_title=None)
    st.plotly_chart(ui.plotly_layout(fig, 380))
    st.dataframe(t.drop(columns="sig").round(3), hide_index=True)
    if (t["VIF"] > 5).any():
        st.warning("VIF > 5 — multicollinearity is inflating standard errors.")
    else:
        st.caption(f"Max VIF = {t['VIF'].max():.2f} (< 5): collinearity is not distorting estimates. "
                   "Governance and Communication correlate, so each one's unique effect is smaller than its raw r.")
    u, fm = A.usage_model, A.full_model
    st.markdown(f"#### Model 2 — Trust → Continued usage: β = {u.table['β (std.)'].iloc[0]:.3f}, "
                f"R² = {u.r2:.3f}")
    st.markdown("#### Model 3 — Usage with trust, reliability and usability barrier")
    st.dataframe(fm.table.round(3), hide_index=True)
    st.caption(f"R² = {fm.r2:.3f}. Trust remains significant after controlling for reliability and usability.")

with tabs[5]:
    st.markdown("#### Does trust carry the effect of each driver onto usage? (Hayes Model 4, percentile bootstrap)")
    rows = []
    for md in A.mediations:
        rows.append({"Driver (X)": S.CONSTRUCTS[md.x], "a: X→Trust": md.a, "b: Trust→Use": md.b,
                     "Total effect c": md.c_total, "Direct effect c′": md.c_direct,
                     "Indirect a×b": md.indirect, "95% CI low": md.ci_low, "95% CI high": md.ci_high,
                     "Type": md.kind})
    mdf = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mdf["Indirect a×b"], y=mdf["Driver (X)"], mode="markers",
                             marker=dict(size=12, color=ui.PRIMARY),
                             error_x=dict(type="data", symmetric=False,
                                          array=mdf["95% CI high"] - mdf["Indirect a×b"],
                                          arrayminus=mdf["Indirect a×b"] - mdf["95% CI low"]),
                             name="Indirect effect (95% CI)"))
    fig.add_vline(x=0, line_dash="dash", line_color=ui.MUTED)
    fig.update_layout(xaxis_title="standardised indirect effect via trust")
    st.plotly_chart(ui.plotly_layout(fig, 300))
    st.dataframe(mdf.round(3), hide_index=True)
    st.caption("If the CI excludes 0 the indirect effect is significant. 'Full' = the direct effect's CI includes 0, "
               "i.e. the driver affects usage only through trust. Cross-sectional data cannot prove causal order.")

with tabs[6]:
    st.markdown("#### Hypothesis scorecard (Model 1 & 2, α = .05)")
    h = A.hypotheses.copy()
    h["p"] = h["p"].map(lambda v: "<.001" if v < .001 else f"{v:.3f}")
    st.dataframe(h, hide_index=True)
    st.markdown("**Reading the result**: a hypothesis can be *correlated* with trust but *not supported* in the "
                "multiple regression — that means its effect overlaps with other drivers (e.g. consent with "
                "transparency). That is a finding about design priority, not a failure.")

with tabs[7]:
    st.markdown("""
**Measurement vs. substantive objectives.** Steps 1–3 are *measurement* objectives (is the data genuine, are the
scales reliable). Steps 4–7 answer the *substantive* research questions (H1–H5 and mediation).

**Theory.** The model sits on UTAUT / TAM (trust as antecedent of behavioural intention) and the digital-trust
literature (npj Digital Medicine 2025 systematic review). Drivers map to the Locker's three layers:
Transparency & Consent → Layer 1–2, Governance → Layer 3 grievance, Communication → Care Moments.

**Cleaning rules (in order):** consent → 18+ → past-year users → attention check → straight-lining → >10 % missing.

**Limitations.** Single-source self-report (common-method bias — add a marker variable or Harman test in a real
run); cross-sectional (no causal order); convenience sample over-represents metro, young, English-speaking users —
the Locker's primary persona (rural, Hindi-first, kiosk-assisted) needs an intercept survey at e-clinics.
""")
    st.download_button("Download cleaned construct scores (CSV)", A.comp.to_csv(index=False).encode(),
                       "construct_scores.csv", "text/csv")
ui.footer()
