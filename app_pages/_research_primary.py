"""Research Lab view for the genuine primary survey (n = 112). Imported by research_lab.py."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import primary as P
from core import ui


@st.cache_data(show_spinner="Running the pre-specified analysis…")
def _results():
    return P.run_all(P.load(), n_boot=5000)  # same settings as the published results


def render():
    st.success("**Genuine primary data.** 112 responses to the Team Anova Google Form (collected 13–17 Jan 2026), "
               "de-identified: names removed, timestamps reduced to dates. Analysis follows the plan fixed in "
               "`docs/primary/ANALYSIS_PLAN.md`; every number here is produced by `core/primary.py`.", icon="✅")
    R = _results()
    n = R["n"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Responses", n["S1"])
    c2.metric("Analytic sample (platform users)", n["A"])
    c3.metric("Items per construct", "2")
    c4.metric("Separate trust measure", "None", help="Q14 combines trust with intention; Q15 measures importance of trust")

    tabs = st.tabs(["1 · Data & sample", "2 · Item results", "3 · Measurement", "4 · Hypotheses",
                    "5 · Unique association", "6 · Sensitivity", "What this can and cannot show"])

    with tabs[0]:
        st.markdown("#### Sample flow")
        st.dataframe(R["flow"], hide_index=True)
        cols = st.columns(3)
        for col, (k, v) in zip(cols, R["profile"].items()):
            fig = px.bar(x=v.values, y=v.index.astype(str), orientation="h", title=f"{k.replace('_', ' ').title()} (users)",
                         color_discrete_sequence=[ui.PRIMARY])
            fig.update_layout(yaxis_title=None, xaxis_title="respondents")
            col.plotly_chart(ui.plotly_layout(fig, 250))
        st.warning("**Not collected:** location (urban / semi-urban / rural), preferred language, use of assisted "
                   "e-clinics or kiosks, digital literacy, and the platform used. The sample (mostly students and employees "
                   "aged 18–35) cannot be assumed to represent ZiffyHealth's rural, Hindi-first, kiosk-assisted patients.")

    with tabs[1]:
        st.markdown("#### How platform users rate current data practices (n = %d)" % n["A"])
        it = R["items"].copy()
        long = it.melt(id_vars=["Item"], value_vars=["% Disagree (1–2)", "% Neutral", "% Agree (4–5)"],
                       var_name="Response", value_name="Share")
        fig = px.bar(long, x="Share", y="Item", color="Response", orientation="h",
                     color_discrete_map={"% Disagree (1–2)": ui.BAD, "% Neutral": "#B8C4CC", "% Agree (4–5)": ui.PRIMARY},
                     category_orders={"Item": list(P.ITEMS)[::-1]})
        fig.update_layout(barmode="stack", xaxis_title="% of users", legend_title=None)
        st.plotly_chart(ui.plotly_layout(fig, 420))
        st.dataframe(it.round(2), hide_index=True)

    with tabs[2]:
        st.markdown("#### Reliability (two-item scales)")
        st.dataframe(R["reliability"].round(3), hide_index=True)
        k = R["kmo"]
        st.markdown(f"**Factorability:** KMO = {k['KMO']:.2f}; Bartlett χ² = {k['Bartlett chi2']:.0f}, df = {k['df']}, "
                    f"p < .001. **Parallel analysis retains {int(R['parallel']['Retain'].sum())} component**, explaining "
                    f"{R['harman_share']:.0%} of item variance.")
        h = R["htmt"].round(2)
        fig = px.imshow(h.values, x=list(h.columns), y=list(h.index), text_auto=".2f", zmin=0, zmax=1.1,
                        color_continuous_scale=["#E3F0F4", "#0F6E8C", "#B3261E"])
        fig.update_layout(title="HTMT discriminant validity (above 0.85 = constructs hard to separate)")
        st.plotly_chart(ui.plotly_layout(fig, 360))
        st.info("Governance and communication are not empirically distinct (HTMT > 1). The ten items share one dominant "
                "factor, consistent with a general favourable or unfavourable view of a platform's data practices, and "
                "possibly with common-method variance. Treat the four constructs as related facets, not independent levers.")

    with tabs[3]:
        st.markdown("#### H1–H4: association of each construct with trust-based continuance intention (Q14)")
        hy = R["hyp"]
        fig = go.Figure(go.Scatter(x=hy["Spearman ρ"], y=hy["H"] + " · " + hy["Construct"], mode="markers",
                                   marker=dict(size=12, color=ui.PRIMARY),
                                   error_x=dict(type="data", symmetric=False, array=hy["CI high"] - hy["Spearman ρ"],
                                                arrayminus=hy["Spearman ρ"] - hy["CI low"])))
        fig.add_vline(x=0, line_dash="dash", line_color=ui.MUTED)
        fig.update_layout(xaxis_title="Spearman ρ with Q14 (95% bootstrap CI)", xaxis_range=[-0.2, 1])
        st.plotly_chart(ui.plotly_layout(fig, 300))
        show = hy.drop(columns=["Code"]).copy()
        show["p (Holm)"] = show["p (Holm)"].map(lambda v: "<.001" if v < .001 else f"{v:.3f}")
        show["p (one-sided)"] = show["p (one-sided)"].map(lambda v: "<.001" if v < .001 else f"{v:.3f}")
        st.dataframe(show.round(3), hide_index=True)
        st.markdown(f"**H5 (trust → continued usage) and mediation: not testable.** The form has no separate measure "
                    f"of trust and of usage intention. Q14 and Q15 correlate at ρ = {R['q14_q15'][0]:.2f} "
                    f"[{R['q14_q15'][1]:.2f}, {R['q14_q15'][2]:.2f}]. That is descriptive only.")

    with tabs[4]:
        o = R["ols"]
        st.markdown(f"#### All four constructs together: OLS on Q14 (HC3 robust SEs), n = {o.n}, R² = {o.r2:.2f}")
        t = o.table
        fig = go.Figure(go.Scatter(x=t["β (std.)"], y=t["Predictor"], mode="markers",
                                   marker=dict(size=12, color=np.where(t["p"] < .05, ui.PRIMARY, "#9FB4BF")),
                                   error_x=dict(type="data", symmetric=False, array=t["β CI high"] - t["β (std.)"],
                                                arrayminus=t["β (std.)"] - t["β CI low"])))
        fig.add_vline(x=0, line_dash="dash", line_color=ui.MUTED)
        fig.update_layout(xaxis_title="standardised β (95% bootstrap CI)")
        st.plotly_chart(ui.plotly_layout(fig, 300))
        st.dataframe(t.round(3), hide_index=True)
        st.markdown("**Robustness, ordinal logistic regression:**")
        st.dataframe(R["ordinal"].round(3), hide_index=True)
        st.caption("Only governance & accountability keeps a unique association once the others are held constant. "
                   "With VIF up to 3.4 and one dominant factor, the other non-significant coefficients mean "
                   "'not separable here', not 'no effect'.")

    with tabs[5]:
        rows = []
        for k, v in R["sensitivity"].items():
            for _, h in v["hyp"].iterrows():
                rows.append({"Sample": {"S1": "All 112", "S2": "Users excl. straight-liners", "S3": "Users excl. duplicates"}[k],
                             "n": v["n"], "Test": h["H"], "ρ": round(h["Spearman ρ"], 3), "Decision": h["Decision"]})
            g = v["ols"].table.set_index("Code").loc["GOV"]
            rows.append({"Sample": rows[-1]["Sample"], "n": v["n"], "Test": "OLS β GOV",
                         "ρ": round(g["β (std.)"], 3), "Decision": f"p = {g['p']:.3f}"})
        st.dataframe(pd.DataFrame(rows), hide_index=True)
        st.markdown("**Exploratory, users vs non-users:**")
        st.dataframe(R["groups"].round(3), hide_index=True)

    with tabs[6]:
        st.markdown("""
**Can show (associations, platform users, n = 74):**
- Users who rate a platform's transparency, consent, governance and communication more favourably also report
  higher trust-based intention to continue using it (H1–H4 supported as associations).
- Perceived governance & accountability has the strongest and only robust unique association.
- Current practices are rated only moderately: just 38% agree their platform protects their data (Q10) or would take
  responsibility for misuse (Q11), and 47% agree it is transparent about who can access their data (Q7).
- 64% say their level of trust strongly influences whether they keep using a platform (Q15).

**Cannot show:**
- Causation (cross-sectional self-report), or that the Locker would change behaviour.
- H5 or mediation through trust (no separate trust measure).
- Which of the four facets matters most beyond governance (one dominant factor; governance and communication not distinct).
- Anything about ZiffyHealth's rural, Hindi-first, kiosk-assisted patients (not sampled; location and language not collected).
- Feature preferences (no Kano or feature questions were asked).

**Statistical power:** with n = 74 the 4-predictor model detects f² ≥ 0.17 and a single unique effect f² ≥ 0.11 at 80% power.
""")
