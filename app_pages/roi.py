from dataclasses import replace

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core import roi, ui

ui.setup("ROI Simulator", "Decision tool · business case",
         "Two value levers — fewer “where is my report?” calls and more repeat visits — against build, "
         "compliance and running costs. Every input is an editable assumption, not ZiffyHealth data.")

a0 = roi.Assumptions()
with st.sidebar:
    st.markdown("### Assumptions")
    clinics = st.slider("Pilot e-clinics", 3, 30, a0.clinics)
    scale = st.slider("Clinics added after month 12", 0, 200, a0.scale_clinics_after_12m, 10)
    ppc = st.slider("Patients / clinic / month", 50, 1000, a0.patients_per_clinic_month, 25)
    uplift = st.slider("Repeat-visit uplift (pp)", 0.0, 10.0, a0.repeat_uplift_pp * 100, 0.5) / 100
    rpv = st.slider("Revenue per visit (₹)", 100, 1500, int(a0.revenue_per_visit), 50)
    margin = st.slider("Contribution margin", 0.1, 0.7, a0.contribution_margin, 0.05)
    calls = st.slider("Status calls per patient", 0.0, 3.0, a0.status_calls_per_patient, 0.1)
    defl = st.slider("Call deflection by Locker", 0.0, 0.9, a0.call_deflection, 0.05)
    cpc = st.slider("Cost per call (₹)", 10, 150, int(a0.cost_per_call), 5)
    build = st.number_input("Build cost (₹)", 0, 10_000_000, int(a0.build_cost), 100_000)
    comp = st.number_input("Compliance setup (₹)", 0, 5_000_000, int(a0.compliance_setup), 50_000)
    run = st.number_input("Fixed run cost / month (₹)", 0, 500_000, int(a0.run_cost_month), 5_000)
    rate = st.slider("Discount rate", 0.05, 0.30, a0.discount_rate_annual, 0.01)

a = replace(a0, clinics=clinics, scale_clinics_after_12m=scale, patients_per_clinic_month=ppc,
            repeat_uplift_pp=uplift, revenue_per_visit=float(rpv), contribution_margin=margin,
            status_calls_per_patient=calls, call_deflection=defl, cost_per_call=float(cpc),
            build_cost=float(build), compliance_setup=float(comp), run_cost_month=float(run),
            discount_rate_annual=rate)
df = roi.monthly_cashflows(a)
s = roi.summary(a)
be = roi.breakeven_uplift(a)

m1, m2, m3, m4 = st.columns(4)
m1.metric("36-month NPV", f"₹{s['npv'] / 1e5:,.1f} L")
m2.metric("Payback", f"month {s['payback']}" if s["payback"] else "not within 36 m")
m3.metric("Gain ÷ cost", f"{s['roi']:.2f}×")
m4.metric("Break-even repeat uplift", f"{be * 100:.1f} pp" if be is not None else "> 30 pp")

fig = go.Figure()
for col, name, color in [("support_saving", "Support-call savings", ui.ACCENT),
                         ("retention_gain", "Repeat-visit contribution", ui.PRIMARY),
                         ("run_cost", "Run cost", "#B8C4CC"), ("messaging_cost", "WhatsApp/SMS", "#D6DEE3"),
                         ("one_time", "One-time (build, compliance, onboarding)", ui.BAD)]:
    fig.add_bar(x=df["month"], y=df[col] / 1e5, name=name, marker_color=color)
fig.add_scatter(x=df["month"], y=df["cumulative"] / 1e5, name="Cumulative net", mode="lines",
                line=dict(color=ui.INK, width=3))
fig.update_layout(barmode="relative", yaxis_title="₹ lakh", xaxis_title="month")
st.plotly_chart(ui.plotly_layout(fig, 420))

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Sensitivity (±25 % on each driver)")
    t = roi.tornado(a)
    tf = go.Figure()
    tf.add_bar(y=t["driver"], x=t["low"] / 1e5, orientation="h", name="−25 %", marker_color=ui.WARN)
    tf.add_bar(y=t["driver"], x=t["high"] / 1e5, orientation="h", name="+25 %", marker_color=ui.PRIMARY)
    tf.update_layout(barmode="overlay", xaxis_title="Δ NPV (₹ lakh)")
    st.plotly_chart(ui.plotly_layout(tf, 380))
with c2:
    st.markdown("#### Risk (Monte Carlo, 1,000 runs)")
    mc = roi.monte_carlo(a, 1000)
    hf = go.Figure(go.Histogram(x=mc / 1e5, nbinsx=40, marker_color=ui.PRIMARY))
    hf.add_vline(x=0, line_dash="dash", line_color=ui.BAD)
    hf.update_layout(xaxis_title="NPV (₹ lakh)", yaxis_title="runs")
    st.plotly_chart(ui.plotly_layout(hf, 330))
    st.metric("Probability NPV > 0", f"{(mc > 0).mean():.0%}")
    st.caption("Uncertain: uplift 0 → 2× base, deflection 0.4 → 1.5× base, build cost 0.8 → 1.8× base, "
               "volume 0.6 → 1.3× base (triangular).")

st.info("**Reading it honestly:** with default assumptions a 10-clinic pilot alone does not repay the build — the "
        "case depends on scaling to more clinics and on call deflection, the most sensitive driver. That is why the "
        "pilot's job is to *measure deflection and repeat rate* against a control group before scaling.")
ui.footer()
