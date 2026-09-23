"""Shared Streamlit UI helpers (styling, banners, small components)."""
from __future__ import annotations

import streamlit as st

PRIMARY = "#0F6E8C"
ACCENT = "#1BA39C"
WARN = "#C9820A"
BAD = "#B3261E"
INK = "#12263A"
MUTED = "#5B6B7A"
SERIES = ["#0F6E8C", "#1BA39C", "#7A5AF8", "#C9820A", "#B3261E", "#5B6B7A"]

CSS = """
<style>
.block-container {padding-top: 3.6rem; max-width: 1180px;}
h1, h2, h3 {letter-spacing: -0.01em;}
.zt-eyebrow {font-size: .78rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
             color: #0F6E8C; margin-bottom: .2rem;}
.zt-lede {font-size: 1.08rem; color: #3C4B59; max-width: 60rem;}
.zt-card {border: 1px solid #DCE6EB; border-radius: 12px; padding: 1rem 1.1rem; background: #FFFFFF; height: 100%;}
.zt-card h4 {margin: 0 0 .35rem 0; font-size: 1rem;}
.zt-card p {margin: 0; color: #3C4B59; font-size: .92rem;}
.zt-pill {display: inline-block; padding: .1rem .55rem; border-radius: 999px; font-size: .75rem;
          font-weight: 600; margin-right: .3rem;}
.zt-pass {background: #E3F4EC; color: #146C43;}
.zt-warn {background: #FDF1DC; color: #8A5A00;}
.zt-fail {background: #FBE3E1; color: #8C1D18;}
.zt-quote {border-left: 3px solid #1BA39C; padding: .3rem .9rem; color: #3C4B59; font-style: italic;}
.zt-table {width: 100%; border-collapse: collapse; font-size: .9rem; margin-bottom: 1rem;}
.zt-table th {text-align: left; background: #F2F7F9; padding: .5rem .6rem; border-bottom: 1px solid #DCE6EB;}
.zt-table td {padding: .5rem .6rem; border-bottom: 1px solid #E5ECEF; vertical-align: top;}
.zt-foot {color: #5B6B7A; font-size: .8rem; margin-top: 2.5rem; border-top: 1px solid #E5ECEF; padding-top: .8rem;}
</style>
"""


def setup(title: str, eyebrow: str, lede: str | None = None) -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f'<div class="zt-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    if lede:
        st.markdown(f'<p class="zt-lede">{lede}</p>', unsafe_allow_html=True)


def card(title: str, body: str) -> None:
    st.markdown(f'<div class="zt-card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)


def pill(status: str, text: str | None = None) -> str:
    cls = {"pass": "zt-pass", "warn": "zt-warn", "fail": "zt-fail"}.get(status, "zt-warn")
    return f'<span class="zt-pill {cls}">{text or status.upper()}</span>'


def synthetic_banner() -> None:
    st.info("**Synthetic demo data.** The bundled survey is simulated from a documented model "
            "(see `core/sample_data.py`). It mirrors the Team Anova questionnaire but contains no real "
            "respondents. Upload your own Google-Forms export to analyse real data.", icon="🧪")


def footer() -> None:
    st.markdown(
        '<div class="zt-foot">Concept prototype by Team Anova (WeSchool GCL live project). '
        'Not affiliated with or endorsed by ZiffyHealth / Ziffytech Solutions Pvt Ltd. '
        'Educational use only — not legal or medical advice.</div>', unsafe_allow_html=True)


def plotly_layout(fig, height: int = 380):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=40, b=10),
                      font=dict(family="sans-serif", size=13, color=INK),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    fig.update_xaxes(gridcolor="#E5ECEF", zeroline=False)
    fig.update_yaxes(gridcolor="#E5ECEF", zeroline=False)
    return fig


def table(df) -> None:
    """Wrapped-text HTML table for prose-heavy frameworks (st.dataframe truncates long cells)."""
    st.markdown(df.to_html(index=False, classes="zt-table", border=0, escape=True), unsafe_allow_html=True)
