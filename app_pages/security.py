import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import locker as LK
from core import ui

ui.setup("Security Architecture", "Solution · data protection by design",
         "The original deck covered only the UX layer of compliance. This page adds the engineering layer: "
         "where health data flows, what can go wrong (STRIDE), which controls stop it, and what happens "
         "in the first 72 hours of a breach.")

st.subheader("1 · Data-flow and trust boundaries")
st.graphviz_chart("""
digraph G {
  rankdir=LR; bgcolor="transparent"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11,
  color="#9FB4BF", fillcolor="#F2F7F9"]; edge [fontname="Helvetica", fontsize=9, color="#5B6B7A"];
  subgraph cluster_edge { label="Untrusted edge (e-clinic / phone)"; style="dashed"; color="#C9820A";
    kiosk [label="IoT kiosk\\n6 vitals + ECG"]; app [label="Patient app /\\nWhatsApp"]; }
  subgraph cluster_core { label="Ziffy trust boundary (India region cloud)"; style="rounded"; color="#0F6E8C";
    gw [label="API gateway\\nmTLS · WAF · rate-limit", fillcolor="#E3F0F4"];
    pe [label="Consent & policy engine\\n(purpose, scope, expiry)", fillcolor="#E3F4EC"];
    ehr [label="Cloud EHR (HL7/FHIR)\\nAES-256 at rest · KMS"];
    ledger [label="Hash-chained audit ledger\\nappend-only · WORM backup", fillcolor="#E3F4EC"];
    notif [label="Care Moments service\\nPHI-free templates"]; grm [label="Grievance service\\ncase IDs · SLA"]; }
  subgraph cluster_partners { label="Processors / partners (contract-bound)"; style="dashed"; color="#7A5AF8";
    doc [label="ZiffyDoc\\n(doctor)"]; lab [label="Diagnostic lab"]; ph [label="Pharmacy"]; abdm [label="ABDM HIE-CM\\n(ABHA)"]; }
  kiosk -> gw [label="TLS 1.3"]; app -> gw [label="TLS 1.3 + OTP"];
  gw -> pe; pe -> ehr [label="allowed reads/writes"]; pe -> ledger [label="every decision"];
  doc -> gw; lab -> gw; ph -> gw; ehr -> abdm [label="consent artefact"];
  pe -> notif; notif -> app [label="'something new is ready'"]; app -> grm; grm -> ledger;
}
""")

st.subheader("2 · STRIDE threat model")
threats = pd.DataFrame([
    ("Spoofing", "Someone uses a patient's phone number or the shared kiosk session", "Kiosk, app login",
     "OTP + session timeout 90 s idle at kiosk; operator cannot view records; device binding", "High"),
    ("Tampering", "Insider edits a log to hide an unauthorised access", "Audit ledger",
     "SHA-256 hash chain + daily anchor of head hash to WORM storage; alert on verify failure", "High"),
    ("Repudiation", "Partner denies having accessed a report", "Lab / pharmacy APIs",
     "Signed API calls per partner; every allow/deny logged with purpose", "Medium"),
    ("Information disclosure", "WhatsApp preview shows 'HIV test positive' on a family phone", "Care Moments",
     "PHI-free templates; content only inside authenticated Locker (checker below)", "High"),
    ("Information disclosure", "Cloud bucket or backup exposed (cf. Star Health 2024 leak)", "EHR storage",
     "Private buckets, KMS keys, tokenised identifiers, DLP scans, vendor audit", "Critical"),
    ("Denial of service", "E-clinic loses connectivity mid-consultation", "Kiosk ↔ cloud",
     "Store-and-forward queue encrypted on device, purged after sync; offline consent capture", "Medium"),
    ("Elevation of privilege", "Pharmacy account reads lab reports", "Policy engine",
     "Purpose + data-type scoping per partner; least privilege; quarterly access review", "High"),
], columns=["STRIDE", "Threat scenario", "Asset / entry point", "Control", "Risk"])
ui.table(threats)

st.subheader("3 · Breach clock — what must happen, by when")
events = [(0, "Detection", "SOC alert / ledger verify fails"), (1, "Contain", "Revoke keys, isolate service"),
          (6, "CERT-In report", "CERT-In Directions 2022 — within 6 h"),
          (24, "Patient notice drafted", "Plain language, what/impact/steps (Rule 7)"),
          (72, "DPB detailed report", "DPDP Rules 2025, Rule 7 — within 72 h"),
          (168, "Post-incident review", "Root cause, control changes, board report")]
fig = go.Figure()
fig.add_trace(go.Scatter(x=[e[0] for e in events], y=[1] * len(events), mode="markers+text",
                         text=[f"<b>{e[1]}</b><br>{e[0]} h" for e in events], textposition="top center",
                         marker=dict(size=14, color=[ui.BAD, ui.WARN, ui.BAD, ui.PRIMARY, ui.BAD, ui.MUTED]),
                         hovertext=[e[2] for e in events], hoverinfo="text"))
fig.update_yaxes(visible=False, range=[0.8, 1.5])
fig.update_xaxes(type="log", title="hours since detection (log scale)", tickvals=[1, 6, 24, 72, 168])
st.plotly_chart(ui.plotly_layout(fig, 260))

st.subheader("4 · PHI-safe notification checker")
st.caption("WhatsApp/SMS previews appear on lock screens and shared family phones. A Care Moment should say "
           "*that* something happened, never *what* it says.")
msg = st.text_area("Draft notification", "Hi Rajesh, your HbA1c result is 8.2 — diabetes uncontrolled. Please consult.")
hits = LK.phi_check(msg)
if hits:
    st.error("Reveals health information: " + ", ".join(f"`{h}`" for h in hits))
    st.success("Safe version: " + LK.safe_rewrite(msg))
else:
    st.success("No sensitive terms detected. Still check that the message names no test, drug or condition.")

st.subheader("5 · Control set mapped to obligations")
ui.table(pd.DataFrame([
    ("Encryption at rest (AES-256, KMS) and in transit (TLS 1.3)", "DPDP Rule 6", "Platform"),
    ("Tokenise ABHA / phone numbers in analytics copies", "DPDP Rule 6 (masking, virtual tokens)", "Platform"),
    ("RBAC + purpose-based consent checks before every read", "DPDP s.6, Rule 6", "Locker L2"),
    ("Access logs ≥ 1 year; security logs 180 days in India; NTP-synced", "DPDP Rule 6; CERT-In", "Locker L2 + SOC"),
    ("Kiosk: auto-logout, no local PHI, privacy filter, tamper-evident enclosure", "Rule 6 reasonable safeguards", "Operations"),
    ("Processor contracts with labs/pharmacies; annual vendor audit", "DPDP s.8(2)", "Legal"),
    ("Breach runbook with 6 h / 72 h clocks and plain-language patient notice", "CERT-In; Rule 7", "SOC + DPO"),
    ("Grievance officer, case IDs, SLA ≤ 30 days (limit 90)", "DPDP s.8(10), s.13", "Locker L3"),
    ("ISO 27001 + ISO 27701 certification roadmap", "Good practice / B2B trust signal", "Leadership"),
], columns=["Control", "Obligation / rationale", "Owner"]))
ui.footer()
