import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import ui

ui.setup("Strategy & ESG", "Case · frameworks tied to decisions",
         "Each framework answers one decision: where the market is going (PESTEL, Five Forces), where Ziffy "
         "can win (strategic groups, ERRC), what to build first (RICE), how trust becomes brand equity (CBBE), "
         "whether the organisation can deliver (7S), how to measure it (Balanced Scorecard) and why it is "
         "material to ESG.")

tabs = st.tabs(["PESTEL", "Five Forces", "Positioning & ERRC", "CBBE", "McKinsey 7S", "RICE", "Scorecard", "ESG"])

with tabs[0]:
    ui.table(pd.DataFrame([
        ("Political", "ABDM push: 96 cr+ ABHA IDs, 110 cr+ linked records (Aug 2026); eSanjeevani 43 cr+ consults",
         "Public rails reward consent-led, interoperable players", "Tailwind"),
        ("Economic", "India digital health ≈ USD 19 bn (2025) → USD 90 bn (2034), 18 % CAGR (IMARC)",
         "Growth is large but price-sensitive in tier-2/3", "Tailwind"),
        ("Social", "82 % of Indian consumers name data protection the top trust factor (PwC 2024); low digital literacy in rural users",
         "Trust must be *visible* and *assisted*, not a policy PDF", "Opportunity"),
        ("Technological", "FHIR/HL7, WhatsApp Business API, IoT vitals kiosks, ABDM HIE-CM",
         "Locker is buildable as an overlay on existing events", "Enabler"),
        ("Environmental", "Tele-consults avoid patient travel; paperless records; cloud energy use",
         "Modest E story — claim only what is measured", "Neutral"),
        ("Legal", "DPDP Rules notified Nov 2025, obligations from May 2027; penalties up to ₹250 cr; CERT-In 6 h reporting",
         "Compliance deadline creates a 2026–27 window to make it a feature", "Urgent"),
    ], columns=["Factor", "Evidence", "Implication for the Locker", "Direction"]))

with tabs[1]:
    forces = pd.DataFrame({"Force": ["Rivalry", "Threat of new entrants", "Buyer power", "Supplier power", "Substitutes"],
                           "Intensity (1–5)": [4.5, 3.5, 4.0, 2.5, 3.5],
                           "Why": ["Practo, Apollo 24|7, Tata 1mg, PharmEasy, MFine + free eSanjeevani",
                                   "Low software barriers; kiosks & franchise network are harder to copy",
                                   "Patients switch apps at zero cost; franchisees choose partners",
                                   "Doctors & labs are plentiful; cloud vendors are commoditised",
                                   "Neighbourhood clinic, pharmacist advice, government AAMs"]})
    fig = go.Figure(go.Scatterpolar(r=list(forces["Intensity (1–5)"]) + [4.5], theta=list(forces["Force"]) + ["Rivalry"],
                                    fill="toself", line=dict(color=ui.PRIMARY)))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5])))
    st.plotly_chart(ui.plotly_layout(fig, 380))
    ui.table(forces)
    st.markdown("**So what:** in a high-rivalry, low-switching-cost market, features are copied fast. A *verifiable* "
                "trust layer tied to the physical e-clinic network is harder to copy and lowers churn.")

with tabs[2]:
    pos = pd.DataFrame({"Player": ["ZiffyHealth (today)", "ZiffyHealth + Locker", "eSanjeevani", "Practo",
                                   "Apollo 24|7", "Tata 1mg"],
                        "Assisted / offline reach": [4.2, 4.2, 4.6, 1.8, 2.8, 2.0],
                        "Patient-visible data control": [1.6, 4.3, 2.8, 2.6, 2.4, 2.1]})
    fig = px.scatter(pos, x="Assisted / offline reach", y="Patient-visible data control", text="Player",
                     color=["Ziffy", "Ziffy", "Other", "Other", "Other", "Other"],
                     color_discrete_map={"Ziffy": ui.PRIMARY, "Other": "#9FB4BF"})
    fig.update_traces(marker=dict(size=16), textposition="top center")
    fig.update_layout(xaxis_range=[1, 5], yaxis_range=[1, 5], showlegend=False)
    st.plotly_chart(ui.plotly_layout(fig, 420))
    st.caption("Strategic-group map — qualitative team judgement from public materials (Sept 2026), not measured data.")
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        ui.card("Eliminate", "Long legal consent forms · 'call the clinic' status chasing")
    with e2:
        ui.card("Reduce", "Text-heavy UI · manual reassurance by doctors · repeated data entry")
    with e3:
        ui.card("Raise", "Consent granularity · speed of grievance response · language coverage")
    with e4:
        ui.card("Create", "Patient-readable access log · Care Moments · verifiable trust status")

with tabs[3]:
    st.markdown("#### Keller's CBBE pyramid — building “Care that Communicates”")
    levels = [("Resonance", "Patients recommend Ziffy clinics; repeat visits; opt in to ABHA linking"),
              ("Judgements · Feelings", "“This is credible and fair” · “I feel safe and respected”"),
              ("Performance · Imagery", "Visible consent, doctor ID, status updates · a clinic that tells you what happens"),
              ("Salience", "“The clinic where you can see your data” — recalled at the moment of need")]
    fig = go.Figure(go.Funnel(y=[l[0] for l in levels], x=[1, 2, 3, 4], text=[l[1] for l in levels],
                              textinfo="text", marker=dict(color=[ui.PRIMARY, ui.ACCENT, "#5FB7C9", "#A9D6E0"])))
    fig.update_layout(showlegend=False)
    st.plotly_chart(ui.plotly_layout(fig, 360))
    st.markdown("**Brand KPI per level:** unaided recall in catchment (salience) · % patients who viewed Locker "
                "(performance) · trust score (judgement) · NPS & 90-day repeat rate (resonance).")

with tabs[4]:
    st.markdown("#### McKinsey 7S — can Ziffy execute the Locker? (drag to score)")
    s7 = {"Strategy": ("Trust as differentiator, not compliance cost", 3), "Structure": ("Named DPO / grievance owner", 2),
          "Systems": ("Event triggers exist (EHR, WhatsApp); consent & ledger do not", 2),
          "Shared values": ("Patient-first, transparent care", 3), "Style": ("Founder-led, fast decisions", 4),
          "Staff": ("Franchise operators need assisted-consent training", 2), "Skills": ("FHIR/ABHA skills present; security ops thin", 2)}
    scores = {}
    cols = st.columns(2)
    for i, (k, (desc, v)) in enumerate(s7.items()):
        scores[k] = cols[i % 2].slider(f"{k} — {desc}", 1, 5, v)
    fig = go.Figure(go.Scatterpolar(r=list(scores.values()) + [list(scores.values())[0]],
                                    theta=list(scores) + [list(scores)[0]], fill="toself", line=dict(color=ui.PRIMARY)))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5])))
    st.plotly_chart(ui.plotly_layout(fig, 380))
    weak = [k for k, v in scores.items() if v <= 2]
    st.markdown(f"**Weakest S's:** {', '.join(weak) or 'none'} — these become pilot pre-requisites "
                "(appoint owner, operator training, consent store + ledger).")
    st.caption("Default scores are the team's outside-in hypothesis; validate with Ziffy leadership.")

with tabs[5]:
    st.markdown("#### RICE prioritisation (edit any cell)")
    rice = pd.DataFrame([
        ("Multilingual consent wizard", 3000, 3, .8, 3), ("Doctor identity card", 3000, 2, .9, 1),
        ("Plain-language access log", 2000, 2, .7, 3), ("Per-partner consent toggles", 1500, 2, .7, 4),
        ("Care Moments (WhatsApp/SMS)", 3000, 3, .8, 3), ("Grievance with case ID", 400, 3, .9, 2),
        ("Audio narration", 900, 2, .5, 2), ("ABHA linking & export", 800, 2, .6, 6),
    ], columns=["Feature", "Reach (patients/qtr)", "Impact (0.25–3)", "Confidence", "Effort (person-weeks)"])
    ed = st.data_editor(rice, hide_index=True, num_rows="fixed")
    ed["RICE"] = (ed.iloc[:, 1] * ed.iloc[:, 2] * ed.iloc[:, 3] / ed.iloc[:, 4]).round(0)
    ed = ed.sort_values("RICE", ascending=False)
    st.plotly_chart(ui.plotly_layout(px.bar(ed, x="RICE", y="Feature", orientation="h",
                                            color_discrete_sequence=[ui.PRIMARY]).update_layout(
        yaxis=dict(categoryorder="total ascending")), 340))
    st.caption("Cross-check with the Kano Analyzer: Must-be features ship regardless of RICE rank.")

with tabs[6]:
    ui.table(pd.DataFrame([
        ("Financial", "Support cost per patient", "−30 % vs control clinics", "Call logs"),
        ("Financial", "90-day repeat-visit rate", "+3 pp vs control", "EHR visit data"),
        ("Customer", "Digital trust score (TRU scale)", "+0.3 on 5-pt scale", "Exit survey"),
        ("Customer", "Consent completion at kiosk", "≥ 95 % in ≤ 3 min", "Wizard analytics"),
        ("Internal process", "Grievances resolved within SLA", "≥ 90 % in 30 days", "Grievance system"),
        ("Internal process", "Ledger integrity checks passed", "100 % daily", "DPO console"),
        ("Learning & growth", "Operators trained on assisted consent", "100 % before go-live", "LMS"),
        ("Learning & growth", "Languages live", "Hindi + Marathi in pilot", "Release notes"),
    ], columns=["Perspective", "KPI", "Pilot target", "Source"]))

with tabs[7]:
    st.markdown("#### Why this is an ESG issue, not just a UX one")
    ui.table(pd.DataFrame([
        ("S", "Customer privacy & data security", "SASB Health Care Delivery — Patient Privacy & EHR; GRI 418",
         "Breaches, complaints substantiated, % records encrypted", "Core — Locker + security architecture"),
        ("S", "Access & affordability", "SDG 3.8 (universal health coverage)", "Patients served in tier-2/3 & rural via kiosks",
         "Assisted, multilingual consent widens safe access"),
        ("S", "Consumer responsibility", "SEBI BRSR Principle 9 (voluntary for unlisted firms)",
         "Consumer complaints received / resolved; data-privacy complaints", "Grievance module produces the metric"),
        ("G", "Data governance & accountability", "DPDP Act; board oversight", "Named DPO; audit findings closed; DPIA done",
         "Ledger + DPO console give auditable evidence"),
        ("G", "Business ethics", "No sale of health data; purpose limitation", "Purpose-denied access attempts", "Policy engine enforces"),
        ("E", "Paper & travel avoided", "GHG Protocol Scope 3 (indicative)", "Paper records avoided; km of travel avoided",
         "Secondary — report only if measured"),
    ], columns=["Pillar", "Material topic", "Standard", "Metric", "Locker contribution"]))
    fig = px.scatter(pd.DataFrame({
        "Topic": ["Patient privacy", "Data security", "Access (rural)", "Grievance handling", "Governance", "Paper/travel"],
        "Impact on business": [4.7, 4.8, 3.8, 3.4, 4.0, 1.8], "Importance to stakeholders": [4.9, 4.6, 4.2, 3.9, 3.6, 2.2]}),
        x="Impact on business", y="Importance to stakeholders", text="Topic", color_discrete_sequence=[ui.PRIMARY])
    fig.update_traces(marker=dict(size=14), textposition="top center")
    fig.update_layout(xaxis_range=[1, 5.2], yaxis_range=[1, 5.2], title="Double-materiality sketch (team judgement)")
    st.plotly_chart(ui.plotly_layout(fig, 420))
ui.footer()
