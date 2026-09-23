import streamlit as st

from core import ui

ui.setup("My Health Data Locker",
         "Team Anova × ZiffyHealth · Digital trust in Indian e-clinics",
         "A trust and visibility layer for a connected digital-health journey: kiosk → doctor → lab → "
         "pharmacy → cloud records. Patients see what is collected, choose who can see it, "
         "watch where it goes, and can act when something is wrong.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("ABHA health IDs created", "96.4 cr", help="ABDM dashboard as reported 12 Aug 2026 (Digital Health News)")
c2.metric("Health records linked to ABHA", "110 cr+", help="Same source")
c3.metric("Max DPDP penalty for weak safeguards", "₹250 cr", help="DPDP Act 2023 Schedule; Rules notified Nov 2025")
c4.metric("Indian consumers: data protection = #1 trust factor", "82%", help="PwC Voice of the Consumer 2024, India")

st.subheader("The problem: three trust breaks in one care journey")
st.write("ZiffyHealth already connects an IoT e-clinic kiosk (6 vitals incl. ECG), tele-consultation, "
         "home diagnostics, pharmacy and a cloud EHR. The care works. What breaks is what the patient "
         "**cannot see** while it happens.")
b1, b2, b3 = st.columns(3)
with b1:
    ui.card("01 · Before care begins",
            "Vitals and personal data are captured at the kiosk with no plain explanation of what is taken, "
            "why, or who the doctor is.<br><em>“What are they taking from me?”</em>")
with b2:
    ui.card("02 · Across hand-offs",
            "Data moves doctor → lab → pharmacy with no visible trail, access history or order status.<br>"
            "<em>“Where did my data go?”</em>")
with b3:
    ui.card("03 · After the consultation",
            "No confirmation of prescription, report or storage — so patients call the franchise operator.<br>"
            "<em>“Did any of this actually happen?”</em>")

st.subheader("The solution: one overlay, three layers")
l1, l2, l3 = st.columns(3)
with l1:
    ui.card("Layer 1 · Explain & Consent",
            "At the kiosk, before vitals: 4-step multilingual consent wizard, doctor identity card, "
            "audio option. Consent is purpose-specific and time-bound (ABDM-style artefact).")
with l2:
    ui.card("Layer 2 · Track & Control",
            "Locker dashboard: plain-language access log backed by a tamper-evident ledger; "
            "per-partner consent toggles enforced by a policy engine before any read.")
with l3:
    ui.card("Layer 3 · Reassure & Resolve",
            "Care Moments on WhatsApp/SMS that never reveal diagnoses, plus grievance tickets with case IDs "
            "and SLA tracking inside DPDP's 90-day limit.")

st.subheader("What is in this toolkit")
tools = [
    ("📊 Research Lab", "Upload a Google-Forms export → data-quality audit, cleaning flow, reliability, "
     "correlations, regression with VIF, bootstrap mediation, hypothesis table."),
    ("🎯 Kano Analyzer", "Classify Locker features as Must-be / Performance / Attractive to decide the pilot MVP."),
    ("🔐 Locker Prototype", "Working patient journey: consent wizard (EN/हिंदी), live policy engine, access log, "
     "Care Moments, grievances, DPO console with ledger verification and a tamper demo."),
    ("🛡️ Security Architecture", "Data-flow, STRIDE threat model, control set, breach clock, PHI-safe notification checker."),
    ("✅ DPDP Readiness", "Score 26 controls from DPDP Act/Rules, CERT-In and ABDM; see which gaps the Locker closes."),
    ("💹 ROI Simulator", "Assumption-driven NPV, payback, tornado sensitivity and Monte Carlo risk for pilot → scale."),
    ("🧭 Strategy & ESG", "PESTEL, Five Forces, 7S readiness, CBBE, ERRC, RICE, Balanced Scorecard, ESG materiality."),
]
cols = st.columns(2)
for i, (t, d) in enumerate(tools):
    with cols[i % 2]:
        ui.card(t, d)
        st.write("")

with st.expander("Honest notes on evidence"):
    st.markdown(
        "- The original project survey could not be re-analysed: the file available failed basic data-quality "
        "tests (item correlations indistinguishable from random answering; minors and non-users included). "
        "No inferential claims from it are used here.\n"
        "- The Research Lab ships with a **synthetic** dataset built on a corrected questionnaire (v2) so the full "
        "pipeline can be demonstrated. Results from it describe the simulation, not Indian patients.\n"
        "- Business-case inputs are editable planning assumptions, not ZiffyHealth figures.\n"
        "- Compliance content is educational; a qualified DPO/counsel must confirm applicability.")
ui.footer()
