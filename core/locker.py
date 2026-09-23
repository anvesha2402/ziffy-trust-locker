"""My Health Data Locker — backend.

A small but real implementation of the three Locker layers:

* Consent store with purpose, scope and expiry (modelled on the ABDM consent
  artefact) and versioned change history.
* Policy engine: every data access by a doctor / lab / pharmacy / insurer is
  checked against live consent *before* it happens (purpose limitation), and
  both allowed and denied attempts are written to the audit ledger.
* Tamper-evident audit ledger: each entry stores the SHA-256 hash of the
  previous entry, so any edit or deletion breaks the chain and is detected.
* Care Moments: downstream events (lab report ready, medicine dispatched…)
  generate PHI-safe notifications.
* Grievance redressal with case IDs and SLA tracking.

SQLite in-memory per session keeps the demo private to each visitor.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
GENESIS = "0" * 64

PARTNERS = {
    "doctor":   {"en": "Treating doctor", "hi": "इलाज करने वाले डॉक्टर",
                 "data": ["vitals", "history", "consult_notes", "prescription", "lab_report"],
                 "purpose": "treatment", "default": True, "required": True},
    "lab":      {"en": "Diagnostic lab", "hi": "जाँच लैब",
                 "data": ["test_order", "lab_report"],
                 "purpose": "diagnostics", "default": True, "required": False},
    "pharmacy": {"en": "Pharmacy partner", "hi": "फ़ार्मेसी",
                 "data": ["prescription"],
                 "purpose": "dispensing", "default": True, "required": False},
    "insurer":  {"en": "Insurance company", "hi": "बीमा कंपनी",
                 "data": ["prescription", "lab_report", "consult_notes"],
                 "purpose": "claims", "default": False, "required": False},
    "research": {"en": "Anonymised research", "hi": "गुमनाम शोध",
                 "data": ["vitals", "lab_report"],
                 "purpose": "research", "default": False, "required": False},
}

DATA_LABELS = {
    "vitals": ("Vitals (BP, pulse, SpO₂, ECG)", "वाइटल्स (बीपी, नब्ज़, ईसीजी)"),
    "history": ("Medical history", "पुरानी बीमारियाँ"),
    "consult_notes": ("Consultation notes", "परामर्श नोट्स"),
    "prescription": ("Prescription", "पर्चा (दवा)"),
    "lab_report": ("Lab report", "जाँच रिपोर्ट"),
    "test_order": ("Test order", "जाँच का ऑर्डर"),
}

ACTORS = {
    "doctor": "Dr. Meera Kulkarni (demo doctor · MBBS, MD)",
    "lab": "Ziffy Wellness Lab, Pune",
    "pharmacy": "Ziffy Pharmacy partner – Hadapsar",
    "insurer": "Demo Health Insurance Ltd.",
    "research": "Anonymised research cohort",
    "operator": "E-clinic operator (kiosk)",
    "dpo": "Data Protection Officer",
    "patient": "Patient (self)",
}

# Care journey: (event code, actor role, data touched, patient-facing text EN, HI)
JOURNEY = [
    ("vitals_recorded", "operator", "vitals", "Your vitals were recorded at the e-clinic.",
     "ई-क्लिनिक पर आपके वाइटल्स दर्ज किए गए।"),
    ("consult_started", "doctor", "vitals", "Your doctor opened your vitals to start the consultation.",
     "परामर्श शुरू करने के लिए डॉक्टर ने आपके वाइटल्स देखे।"),
    ("consult_done", "doctor", "consult_notes", "Consultation completed. Notes saved to your Locker.",
     "परामर्श पूरा हुआ। नोट्स आपके लॉकर में सेव हैं।"),
    ("rx_issued", "doctor", "prescription", "Your prescription is ready in your Locker.",
     "आपका पर्चा लॉकर में तैयार है।"),
    ("lab_ordered", "lab", "test_order", "The lab received your test order.",
     "लैब को आपकी जाँच का ऑर्डर मिल गया।"),
    ("report_ready", "lab", "lab_report", "A new report is ready in your Locker.",
     "आपकी नई रिपोर्ट लॉकर में तैयार है।"),
    ("rx_to_pharmacy", "pharmacy", "prescription", "The pharmacy received your prescription.",
     "फ़ार्मेसी को आपका पर्चा मिल गया।"),
    ("claim_requested", "insurer", "lab_report", "An insurer asked to see your report.",
     "एक बीमा कंपनी ने आपकी रिपोर्ट देखने का अनुरोध किया।"),
]

GRIEVANCE_CATEGORIES = [
    "Someone accessed my data without reason",
    "Wrong information in my record",
    "I want my data deleted",
    "I did not get my report / medicine",
    "Consent was taken without explanation",
    "Other",
]
SLA_DAYS = {"ack": 2, "resolve": 30}  # internal SLA — well inside DPDP's 90-day outer limit


def _now() -> datetime:
    return datetime.now(IST)


def _canon(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), default=str)


@dataclass
class AccessDecision:
    allowed: bool
    reason: str
    entry_hash: str


class Locker:
    def __init__(self, patient_name: str = "Rajesh Kumar", patient_id: str = "ZH-PT-10482"):
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.patient_name = patient_name
        self.patient_id = patient_id
        self._schema()
        self.journey_step = 0

    # ------------------------------------------------------------ schema
    def _schema(self):
        self.db.executescript("""
        CREATE TABLE consent(
            partner TEXT PRIMARY KEY, granted INTEGER, purpose TEXT,
            data_types TEXT, expires TEXT, version INTEGER, updated TEXT);
        CREATE TABLE consent_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT, partner TEXT, granted INTEGER,
            version INTEGER, ts TEXT, via TEXT);
        CREATE TABLE ledger(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, actor_role TEXT, actor TEXT,
            action TEXT, resource TEXT, purpose TEXT, outcome TEXT, detail TEXT,
            prev_hash TEXT, hash TEXT);
        CREATE TABLE moments(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, code TEXT, text_en TEXT,
            text_hi TEXT, status TEXT);
        CREATE TABLE grievance(
            case_id TEXT PRIMARY KEY, ts TEXT, category TEXT, description TEXT,
            status TEXT, ack_due TEXT, resolve_due TEXT, updates TEXT);
        """)

    # ------------------------------------------------------------ ledger
    def _last_hash(self) -> str:
        row = self.db.execute("SELECT hash FROM ledger ORDER BY seq DESC LIMIT 1").fetchone()
        return row["hash"] if row else GENESIS

    def log(self, actor_role: str, action: str, resource: str = "", purpose: str = "",
            outcome: str = "ok", detail: str = "") -> str:
        prev = self._last_hash()
        entry = {"ts": _now().isoformat(timespec="seconds"), "actor_role": actor_role,
                 "actor": ACTORS.get(actor_role, actor_role), "action": action,
                 "resource": resource, "purpose": purpose, "outcome": outcome,
                 "detail": detail, "prev_hash": prev}
        h = hashlib.sha256(_canon(entry).encode()).hexdigest()
        self.db.execute(
            "INSERT INTO ledger(ts,actor_role,actor,action,resource,purpose,outcome,detail,prev_hash,hash)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)",
            (entry["ts"], actor_role, entry["actor"], action, resource, purpose, outcome, detail, prev, h))
        self.db.commit()
        return h

    def verify_chain(self) -> tuple[bool, int | None]:
        """Recompute every hash. Returns (ok, first_bad_seq)."""
        prev = GENESIS
        for r in self.db.execute("SELECT * FROM ledger ORDER BY seq"):
            entry = {k: r[k] for k in ("ts", "actor_role", "actor", "action", "resource",
                                        "purpose", "outcome", "detail")}
            entry["prev_hash"] = prev
            h = hashlib.sha256(_canon(entry).encode()).hexdigest()
            if r["prev_hash"] != prev or r["hash"] != h:
                return False, r["seq"]
            prev = r["hash"]
        return True, None

    def tamper(self, seq: int, new_detail: str = "edited by insider") -> None:
        """Demo only: silently edit a past ledger row as a malicious insider would."""
        self.db.execute("UPDATE ledger SET detail=? WHERE seq=?", (new_detail, seq))
        self.db.commit()

    def ledger(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM ledger ORDER BY seq")]

    # ------------------------------------------------------------ consent
    def give_initial_consent(self, choices: dict[str, bool], language: str, via: str = "kiosk") -> None:
        exp = (_now() + timedelta(days=365)).date().isoformat()
        for p, meta in PARTNERS.items():
            granted = bool(choices.get(p, meta["default"])) or meta["required"]
            self.db.execute(
                "INSERT OR REPLACE INTO consent VALUES(?,?,?,?,?,?,?)",
                (p, int(granted), meta["purpose"], ",".join(meta["data"]), exp, 1,
                 _now().isoformat(timespec="seconds")))
            self.db.execute("INSERT INTO consent_history(partner,granted,version,ts,via) VALUES(?,?,?,?,?)",
                            (p, int(granted), 1, _now().isoformat(timespec="seconds"), via))
        self.db.commit()
        granted = [p for p, v in self.consents().items() if v["granted"]]
        self.log("patient", "consent_given", ",".join(granted), "registration",
                 detail=f"language={language}; via={via}; expires={exp}")

    def has_consented(self) -> bool:
        return self.db.execute("SELECT COUNT(*) c FROM consent").fetchone()["c"] > 0

    def consents(self) -> dict[str, dict]:
        return {r["partner"]: dict(r) | {"granted": bool(r["granted"])}
                for r in self.db.execute("SELECT * FROM consent")}

    def set_consent(self, partner: str, granted: bool, via: str = "locker_app") -> None:
        if PARTNERS[partner]["required"] and not granted:
            raise ValueError("Treating-doctor access is needed to provide care. "
                             "To stop it, end the care relationship or raise a grievance.")
        cur = self.consents()[partner]
        if cur["granted"] == granted:
            return
        v = cur["version"] + 1
        self.db.execute("UPDATE consent SET granted=?, version=?, updated=? WHERE partner=?",
                        (int(granted), v, _now().isoformat(timespec="seconds"), partner))
        self.db.execute("INSERT INTO consent_history(partner,granted,version,ts,via) VALUES(?,?,?,?,?)",
                        (partner, int(granted), v, _now().isoformat(timespec="seconds"), via))
        self.db.commit()
        self.log("patient", "consent_granted" if granted else "consent_withdrawn", partner,
                 PARTNERS[partner]["purpose"], detail=f"version={v}")

    def consent_history(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM consent_history ORDER BY id")]

    # ------------------------------------------------------------ policy engine
    def request_access(self, actor_role: str, data_type: str, purpose: str | None = None) -> AccessDecision:
        """Check consent + purpose + expiry, then log the attempt either way."""
        if actor_role in ("operator", "patient", "dpo"):
            h = self.log(actor_role, "read" if actor_role != "operator" else "write", data_type,
                         purpose or "care_delivery")
            return AccessDecision(True, "Operational access (logged)", h)
        c = self.consents().get(actor_role)
        purpose = purpose or PARTNERS[actor_role]["purpose"]
        if c is None:
            reason = "No consent on record"
        elif not c["granted"]:
            reason = ("Patient did not allow this partner" if c["version"] == 1
                      else "Patient has withdrawn consent")
        elif purpose != c["purpose"]:
            reason = f"Purpose '{purpose}' not covered (consented: {c['purpose']})"
        elif data_type not in c["data_types"].split(","):
            reason = f"'{data_type}' not in consented data types"
        elif c["expires"] < _now().date().isoformat():
            reason = "Consent expired"
        else:
            h = self.log(actor_role, "read", data_type, purpose, "allowed")
            return AccessDecision(True, "Consent valid", h)
        h = self.log(actor_role, "read", data_type, purpose, "denied", reason)
        return AccessDecision(False, reason, h)

    # ------------------------------------------------------------ care moments
    def advance_journey(self) -> dict | None:
        if self.journey_step >= len(JOURNEY):
            return None
        code, role, data, en, hi = JOURNEY[self.journey_step]
        self.journey_step += 1
        decision = self.request_access(role, data)
        status = "delivered" if decision.allowed else "blocked"
        if not decision.allowed:
            en = f"Blocked: {ACTORS[role]} tried to access your {DATA_LABELS[data][0].lower()} — " \
                 f"you have not allowed this. No data was shared."
            hi = f"रोका गया: {PARTNERS.get(role, {}).get('hi', role)} ने आपका डेटा देखने की कोशिश की — " \
                 f"आपने अनुमति नहीं दी है। कोई डेटा साझा नहीं हुआ।"
        self.db.execute("INSERT INTO moments(ts,code,text_en,text_hi,status) VALUES(?,?,?,?,?)",
                        (_now().isoformat(timespec="seconds"), code, en, hi, status))
        self.db.commit()
        return {"code": code, "role": role, "data": data, "allowed": decision.allowed,
                "reason": decision.reason, "en": en, "hi": hi}

    def moments(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM moments ORDER BY id DESC")]

    # ------------------------------------------------------------ grievance
    def raise_grievance(self, category: str, description: str) -> str:
        case_id = "ZG-" + _now().strftime("%y%m%d") + "-" + uuid.uuid4().hex[:5].upper()
        now = _now()
        updates = [{"ts": now.isoformat(timespec="seconds"), "status": "Received",
                    "note": "Your complaint is registered. The Grievance Officer will respond."}]
        self.db.execute("INSERT INTO grievance VALUES(?,?,?,?,?,?,?,?)",
                        (case_id, now.isoformat(timespec="seconds"), category, description, "Received",
                         (now + timedelta(days=SLA_DAYS["ack"])).date().isoformat(),
                         (now + timedelta(days=SLA_DAYS["resolve"])).date().isoformat(),
                         json.dumps(updates)))
        self.db.commit()
        self.log("patient", "grievance_raised", case_id, "grievance_redressal", detail=category)
        return case_id

    def update_grievance(self, case_id: str, status: str, note: str) -> None:
        row = self.db.execute("SELECT updates FROM grievance WHERE case_id=?", (case_id,)).fetchone()
        ups = json.loads(row["updates"])
        ups.append({"ts": _now().isoformat(timespec="seconds"), "status": status, "note": note})
        self.db.execute("UPDATE grievance SET status=?, updates=? WHERE case_id=?",
                        (status, json.dumps(ups), case_id))
        self.db.commit()
        self.log("dpo", "grievance_updated", case_id, "grievance_redressal", detail=status)

    def grievances(self) -> list[dict]:
        out = []
        for r in self.db.execute("SELECT * FROM grievance ORDER BY ts DESC"):
            d = dict(r)
            d["updates"] = json.loads(d["updates"])
            out.append(d)
        return out

    # ------------------------------------------------------------ helpers
    def plain_language_log(self, lang: str = "en") -> list[dict]:
        """Turn raw ledger rows into sentences a patient can read."""
        rows = []
        for r in self.ledger():
            role, act, res, out = r["actor_role"], r["action"], r["resource"], r["outcome"]
            who = ACTORS.get(role, role)
            what = DATA_LABELS.get(res, (res, res))[0 if lang == "en" else 1]
            if act == "read" and out == "allowed":
                s = f"{who} viewed your {what.lower()}" if lang == "en" else f"{who} ने आपकी {what} देखी"
            elif act == "read" and out == "denied":
                s = (f"{who} was BLOCKED from your {what.lower()} ({r['detail']})" if lang == "en"
                     else f"{who} को आपकी {what} देखने से रोका गया")
            elif act == "write":
                s = f"{who} recorded your {what.lower()}" if lang == "en" else f"{who} ने आपकी {what} दर्ज की"
            elif act == "consent_given":
                s = "You gave consent at registration" if lang == "en" else "आपने पंजीकरण पर सहमति दी"
            elif act == "consent_withdrawn":
                s = (f"You stopped {PARTNERS[res]['en'].lower()} from seeing your data" if lang == "en"
                     else f"आपने {PARTNERS[res]['hi']} की अनुमति हटाई")
            elif act == "consent_granted":
                s = (f"You allowed {PARTNERS[res]['en'].lower()} to see your data" if lang == "en"
                     else f"आपने {PARTNERS[res]['hi']} को अनुमति दी")
            elif act == "grievance_raised":
                s = f"You raised complaint {res}" if lang == "en" else f"आपने शिकायत {res} दर्ज की"
            elif act == "grievance_updated":
                s = f"Complaint {res} updated: {r['detail']}" if lang == "en" else f"शिकायत {res} अपडेट: {r['detail']}"
            else:
                s = f"{who}: {act} {res}"
            rows.append({"When": r["ts"].replace("T", " ")[:16], "What happened": s,
                         "Outcome": out, "Proof (hash)": r["hash"][:12] + "…"})
        return rows[::-1]


# ------------------------------------------------------------ PHI-safe notifications
SENSITIVE_TERMS = [
    "hiv", "aids", "cancer", "tumour", "tumor", "diabetes", "hba1c", "pregnan", "tb ",
    "tuberculosis", "hepatitis", "std", "sti", "psychiat", "depress", "anxiety", "bipolar",
    "schizo", "ecg abnormal", "positive", "negative", "biopsy", "chemo", "insulin", "thyroid",
    "infertil", "abortion", "mtp", "dialysis", "covid", "result:", "diagnos",
]


def phi_check(message: str) -> list[str]:
    """Flag words that reveal health conditions or results in a notification preview.

    WhatsApp/SMS previews show on lock screens and shared family phones, so a
    Care Moment must say *that* something happened, never *what* it says.
    """
    m = " " + message.lower() + " "
    return sorted({t.strip() for t in SENSITIVE_TERMS if t in m})


def safe_rewrite(message: str) -> str:
    return "Update from Ziffy: something new is ready in your Health Locker. Open the app to view it securely."
