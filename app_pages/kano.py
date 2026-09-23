from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from core import kano, ui

DATA = Path(__file__).resolve().parents[1] / "data"
ui.setup("Kano Analyzer", "Evidence · feature prioritisation",
         "Which Locker features must ship in the pilot, and which are delighters? Each respondent answers a "
         "functional (“if the Locker had X…”) and dysfunctional (“if it did not…”) question per feature.")

src = st.radio("Data", ["Synthetic demo (110 respondents)", "Upload CSV"], horizontal=True)
if src.startswith("Synthetic"):
    df = pd.read_csv(DATA / "kano_responses_SYNTHETIC.csv")
    ui.synthetic_banner()
else:
    up = st.file_uploader("Long format: respondent_id, feature, functional, dysfunctional", type="csv")
    if up is None:
        st.stop()
    df = pd.read_csv(up)

res = kano.analyse(df)
fig = px.scatter(res, x="Better (satisfaction)", y=res["Worse (dissatisfaction)"].abs(), text="feature",
                 color="Category", size="n", size_max=18,
                 color_discrete_sequence=ui.SERIES, labels={"y": "|Worse| (dissatisfaction if absent)"})
fig.add_hline(y=0.5, line_dash="dot", line_color=ui.MUTED)
fig.add_vline(x=0.5, line_dash="dot", line_color=ui.MUTED)
for x, y, t in [(.25, .95, "Must-be"), (.8, .95, "Performance"), (.8, .05, "Attractive"), (.25, .05, "Indifferent")]:
    fig.add_annotation(x=x, y=y, text=t, showarrow=False, font=dict(color=ui.MUTED))
fig.update_traces(textposition="top center")
fig.update_layout(xaxis_range=[0, 1], yaxis_range=[0, 1])
st.plotly_chart(ui.plotly_layout(fig, 520))

st.subheader("Roadmap implied")
g = kano.mvp_recommendation(res)
cols = st.columns(4)
for c, (k, v) in zip(cols, g.items()):
    with c:
        ui.card(k, "<br>".join(f"• {x}" for x in v) or "—")
st.dataframe(res, hide_index=True)
with st.expander("Kano question template"):
    st.markdown("- **Functional:** *If the Locker showed you who viewed your records, how would you feel?*\n"
                "- **Dysfunctional:** *If the Locker did NOT show you who viewed your records, how would you feel?*\n"
                "- Answers: I like it · I expect it · I am neutral · I can live with it · I dislike it\n\n"
                "Better = (A+O)/(A+O+M+I); Worse = −(O+M)/(A+O+M+I) (Berger et al., 1993).")
ui.footer()
