"""DPDP readiness self-assessment.

Controls are drawn from the Digital Personal Data Protection Act, 2023, the
DPDP Rules, 2025 (notified Nov 2025; most obligations apply from May 2027),
the CERT-In Directions (April 2022) and the ABDM consent framework.

Educational tool, not legal advice. References are to the section / rule that
motivates each control; qualified counsel / a DPO must confirm applicability.
"""
from __future__ import annotations

import pandas as pd

LEVELS = {0: "Not in place", 1: "Partial", 2: "In place"}

# (id, domain, control, reference, weight 1-3, locker_layer or None)
CONTROLS = [
    ("N1", "Notice & Consent", "Standalone notice in plain language before data collection, listing data items and purposes",
     "DPDP s.5; Rule 3", 3, "L1"),
    ("N2", "Notice & Consent", "Notice and consent available in English and Eighth-Schedule languages the patient understands",
     "DPDP s.5(3)", 2, "L1"),
    ("N3", "Notice & Consent", "Consent is specific per purpose and per recipient (doctor / lab / pharmacy / insurer)",
     "DPDP s.6(1); ABDM consent artefact", 3, "L2"),
    ("N4", "Notice & Consent", "Withdrawing consent is as easy as giving it, and takes effect across partners",
     "DPDP s.6(4)–(6)", 3, "L2"),
    ("N5", "Notice & Consent", "Consent records kept with timestamp, version and channel (kiosk / app)",
     "DPDP s.6(10) burden of proof", 2, "L1"),
    ("R1", "Data Principal Rights", "Patient can see a summary of data held and who it was shared with",
     "DPDP s.11", 3, "L2"),
    ("R2", "Data Principal Rights", "Correction, completion and erasure requests can be raised and tracked",
     "DPDP s.12", 2, "L3"),
    ("R3", "Data Principal Rights", "Nomination of another person to exercise rights (death / incapacity)",
     "DPDP s.14", 1, None),
    ("R4", "Data Principal Rights", "Grievance mechanism with case ID and response inside the prescribed period (max 90 days)",
     "DPDP s.13; Rules", 3, "L3"),
    ("S1", "Security Safeguards", "Encryption of health data at rest and in transit; masking / tokenisation of identifiers",
     "DPDP s.8(5); Rule 6", 3, None),
    ("S2", "Security Safeguards", "Role-based access control; least privilege for clinic operators and partners",
     "Rule 6", 3, "L2"),
    ("S3", "Security Safeguards", "Access logs that record who accessed what and when, retained ≥ 1 year",
     "Rule 6", 3, "L2"),
    ("S4", "Security Safeguards", "Kiosk hardening: auto-logout, no local storage of PHI, privacy screen",
     "Rule 6 (reasonable safeguards)", 2, None),
    ("S5", "Security Safeguards", "Backups and tested recovery for EHR and consent store",
     "Rule 6", 2, None),
    ("B1", "Breach Response", "Incident reported to CERT-In within 6 hours of detection",
     "CERT-In Directions 2022", 3, None),
    ("B2", "Breach Response", "Detailed breach report to the Data Protection Board within 72 hours",
     "DPDP s.8(6); Rule 7", 3, None),
    ("B3", "Breach Response", "Affected patients informed without delay in plain language",
     "Rule 7", 2, "L3"),
    ("B4", "Breach Response", "Security logs kept in India for 180 days; clocks synced to NTP",
     "CERT-In Directions 2022", 2, None),
    ("G1", "Governance & Accountability", "Named Grievance / Data Protection Officer with published contact details",
     "DPDP s.8(9), s.10", 2, "L3"),
    ("G2", "Governance & Accountability", "Data Protection Impact Assessment and periodic audit (if notified as Significant Data Fiduciary)",
     "DPDP s.10", 2, None),
    ("G3", "Governance & Accountability", "Contracts with labs, pharmacies and cloud vendors bind them as processors",
     "DPDP s.8(2)", 3, None),
    ("G4", "Governance & Accountability", "Board-level privacy KPIs (consent rate, grievances, breaches) reviewed quarterly",
     "Good practice / ESG", 1, "L3"),
    ("D1", "Retention & Minimisation", "Only data needed for the stated purpose is collected at the kiosk",
     "DPDP s.6(1)", 2, "L1"),
    ("D2", "Retention & Minimisation", "Data erased when purpose is served or consent withdrawn, subject to medical-record retention law",
     "DPDP s.8(7)", 2, None),
    ("A1", "ABDM Interoperability", "ABHA linking and HIP/HIU flows use ABDM consent artefacts with purpose and expiry",
     "ABDM HIE-CM", 2, "L2"),
    ("A2", "ABDM Interoperability", "Records exchanged in FHIR format with encryption in transit",
     "ABDM / NDHB standards", 1, None),
]

DOMAINS = list(dict.fromkeys(c[1] for c in CONTROLS))


def controls_df() -> pd.DataFrame:
    return pd.DataFrame(CONTROLS, columns=["ID", "Domain", "Control", "Reference", "Weight", "Locker"])


def score(levels: dict[str, int], with_locker: bool = False) -> pd.DataFrame:
    df = controls_df()
    df["Level"] = df["ID"].map(levels).fillna(0).astype(int)
    if with_locker:
        df.loc[df["Locker"].notna(), "Level"] = 2
    df["Points"] = df["Level"] * df["Weight"]
    df["Max"] = 2 * df["Weight"]
    return df


def domain_scores(scored: pd.DataFrame) -> pd.DataFrame:
    g = scored.groupby("Domain", sort=False)[["Points", "Max"]].sum()
    g["Score %"] = (100 * g["Points"] / g["Max"]).round(0)
    return g.reset_index()


def overall(scored: pd.DataFrame) -> float:
    return round(100 * scored["Points"].sum() / scored["Max"].sum(), 1)


def gaps(scored: pd.DataFrame) -> pd.DataFrame:
    g = scored[scored["Level"] < 2].copy()
    g["Gap severity"] = (2 - g["Level"]) * g["Weight"]
    g["Closed by Locker?"] = g["Locker"].map(
        {"L1": "Yes – Layer 1 (Explain & Consent)", "L2": "Yes – Layer 2 (Track & Control)",
         "L3": "Yes – Layer 3 (Reassure & Resolve)"}).fillna("No – back-end / policy work")
    return g.sort_values("Gap severity", ascending=False)[
        ["ID", "Domain", "Control", "Reference", "Level", "Gap severity", "Closed by Locker?"]]


def readiness_band(pct: float) -> str:
    if pct >= 80:
        return "Ready"
    if pct >= 60:
        return "Largely ready — close priority gaps"
    if pct >= 40:
        return "Partially ready — structured programme needed"
    return "Early stage — high regulatory exposure"
