import plotly.graph_objects as go
import streamlit as st

from core import dpdp, ui

ui.setup("DPDP Readiness Assessor", "Decision tool · compliance",
         "Score 26 controls drawn from the DPDP Act 2023, DPDP Rules 2025, CERT-In Directions and ABDM. "
         "See the overall readiness, the priority gaps, and how much the Locker closes on its own.")
st.caption("Timeline: Rules notified Nov 2025 · consent-manager provisions from 13 Nov 2026 · most obligations "
           "from 13 May 2027. Educational tool — not legal advice.")

df = dpdp.controls_df()
preset = st.radio("Start from", ["All 'Partial' (typical early-stage)", "All 'Not in place'", "Blank — I'll score"],
                  horizontal=True)
start = {"All 'Partial' (typical early-stage)": 1, "All 'Not in place'": 0, "Blank — I'll score": 0}[preset]

levels = {}
for dom in dpdp.DOMAINS:
    with st.expander(dom, expanded=False):
        for _, r in df[df["Domain"] == dom].iterrows():
            c1, c2 = st.columns([4, 2])
            c1.markdown(f"**{r['ID']}** {r['Control']}  \n<span style='color:#5B6B7A;font-size:.85rem'>{r['Reference']}"
                        f"{' · Locker ' + str(r['Locker']) if isinstance(r['Locker'], str) else ''}</span>", unsafe_allow_html=True)
            levels[r["ID"]] = c2.select_slider(" ", options=[0, 1, 2], value=start, key=f"{preset}_{r['ID']}",
                                               format_func=lambda v: dpdp.LEVELS[v], label_visibility="collapsed")

now = dpdp.score(levels)
with_l = dpdp.score(levels, with_locker=True)
o1, o2 = dpdp.overall(now), dpdp.overall(with_l)
m1, m2, m3 = st.columns(3)
m1.metric("Readiness today", f"{o1:.0f}%", dpdp.readiness_band(o1), delta_color="off")
m2.metric("With the Locker", f"{o2:.0f}%", f"+{o2 - o1:.0f} pts")
m3.metric("Open gaps", int((now["Level"] < 2).sum()))

d1, d2 = dpdp.domain_scores(now), dpdp.domain_scores(with_l)
fig = go.Figure()
for d, name, color in [(d1, "Today", ui.WARN), (d2, "With Locker", ui.PRIMARY)]:
    fig.add_trace(go.Scatterpolar(r=list(d["Score %"]) + [d["Score %"].iloc[0]],
                                  theta=list(d["Domain"]) + [d["Domain"].iloc[0]], name=name, fill="toself",
                                  line=dict(color=color), opacity=.75))
fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])))
st.plotly_chart(ui.plotly_layout(fig, 460))

st.subheader("Priority gap list")
st.caption("Severity = (2 − level) × weight. Gaps the Locker does not close need back-end, legal or process work.")
st.dataframe(dpdp.gaps(now), hide_index=True)
ui.footer()
