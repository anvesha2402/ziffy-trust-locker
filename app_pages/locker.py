import pandas as pd
import streamlit as st

from core import locker as LK
from core import ui

ui.setup("Locker Prototype", "Solution · working prototype",
         "Walk through Rajesh's e-clinic visit. Every data access is checked against his consent "
         "before it happens, and every attempt — allowed or blocked — is written to a tamper-evident ledger.")

if "locker" not in st.session_state:
    st.session_state.locker = LK.Locker()
L: LK.Locker = st.session_state.locker

with st.sidebar:
    st.markdown("**Persona** · Rajesh Kumar, 45, semi-urban, Hindi-first, managing hypertension, "
                "visits a Ziffy e-clinic with kiosk-operator help.")
    lang = st.radio("Language / भाषा", ["English", "हिंदी"], horizontal=True)
    if st.button("↺ Reset demo"):
        st.session_state.locker = LK.Locker()
        st.session_state.pop("wiz", None)
        st.rerun()
HI = lang == "हिंदी"
T = (lambda en, hi: hi if HI else en)

role = st.segmented_control("View as", ["Patient (kiosk & app)", "Care partners", "DPO console"],
                            default="Patient (kiosk & app)")

# ------------------------------------------------------------------ PATIENT
if role == "Patient (kiosk & app)":
    if not L.has_consented():
        st.subheader(T("Layer 1 · Explain & Consent — at the kiosk, before vitals", "परत 1 · समझाएँ और सहमति लें"))
        step = st.session_state.setdefault("wiz", 1)
        st.progress(step / 4, text=T(f"Step {step} of 4", f"चरण {step} / 4"))
        if step == 1:
            st.markdown(T("### 👋 Welcome, Rajesh\nBefore we measure your vitals, here is **what we will collect** and why.",
                          "### 👋 नमस्ते, राजेश जी\nवाइटल्स मापने से पहले, हम बताते हैं कि **क्या लेंगे** और क्यों।"))
            for k in ["vitals", "history", "consult_notes", "prescription", "lab_report"]:
                st.markdown(f"- {LK.DATA_LABELS[k][1 if HI else 0]}")
            st.caption(T("Purpose: only to treat you. Nothing is sold. You can change your choices any time.",
                         "उद्देश्य: सिर्फ़ आपका इलाज। कुछ भी बेचा नहीं जाता। आप कभी भी बदलाव कर सकते हैं।"))
            st.button(T("🔊 Listen (audio narration — proposed)", "🔊 सुनें (ऑडियो — प्रस्तावित)"), disabled=True)
        elif step == 2:
            st.markdown(T("### 🩺 Your doctor today", "### 🩺 आज आपके डॉक्टर"))
            c1, c2 = st.columns([1, 3])
            c1.markdown("<div style='font-size:64px;text-align:center'>👩‍⚕️</div>", unsafe_allow_html=True)
            c2.markdown(f"**{LK.ACTORS['doctor']}**  \n"
                        + T("General physician · 12 yrs experience · Registration verified ✓ (demo)",
                            "सामान्य चिकित्सक · 12 वर्ष अनुभव · पंजीकरण सत्यापित ✓ (डेमो)"))
            st.info(T("Only this doctor sees your vitals during the consultation.",
                      "परामर्श के दौरान सिर्फ़ यही डॉक्टर आपके वाइटल्स देखेंगी।"))
        elif step == 3:
            st.markdown(T("### 🔀 Who else may see your data?", "### 🔀 और कौन आपका डेटा देख सकता है?"))
            choices = {}
            for p, meta in LK.PARTNERS.items():
                label = f"{meta['hi' if HI else 'en']} — " + ", ".join(
                    LK.DATA_LABELS[d][1 if HI else 0] for d in meta["data"])
                choices[p] = st.toggle(label, value=meta["default"], disabled=meta["required"], key=f"c_{p}")
            st.session_state.choices = choices
            st.caption(T("Treating doctor access is needed for care. Everything else is your choice.",
                         "इलाज के लिए डॉक्टर की अनुमति ज़रूरी है। बाक़ी सब आपकी मर्ज़ी।"))
        elif step == 4:
            st.markdown(T("### ✅ Confirm", "### ✅ पुष्टि करें"))
            ch = st.session_state.get("choices", {p: m["default"] for p, m in LK.PARTNERS.items()})
            for p, v in ch.items():
                st.markdown(f"- {'✅' if v or LK.PARTNERS[p]['required'] else '⛔'} {LK.PARTNERS[p]['hi' if HI else 'en']}")
            st.caption(T("Valid for 12 months. Withdraw any time from your Locker. A copy is sent to you.",
                         "12 महीने के लिए मान्य। लॉकर से कभी भी वापस लें। इसकी कॉपी आपको भेजी जाएगी।"))
            if st.button(T("I agree — start my visit", "मैं सहमत हूँ — जाँच शुरू करें"), type="primary"):
                L.give_initial_consent(ch, "hi" if HI else "en")
                st.rerun()
        b1, b2, _ = st.columns([1, 1, 4])
        if step > 1 and b1.button(T("← Back", "← पीछे")):
            st.session_state.wiz -= 1
            st.rerun()
        if step < 4 and b2.button(T("Next →", "आगे →"), type="primary"):
            st.session_state.wiz += 1
            st.rerun()
        st.stop()

    # Locker home ------------------------------------------------------------
    st.subheader(T("My Health Data Locker", "मेरा हेल्थ डेटा लॉकर"))
    ok, _ = L.verify_chain()
    s1, s2, s3, s4 = st.columns(4)
    s1.metric(T("Care events", "देखभाल घटनाएँ"), len(L.moments()))
    s2.metric(T("Partners allowed", "अनुमति प्राप्त"), sum(v["granted"] for v in L.consents().values()))
    s3.metric(T("Blocked attempts", "रोके गए प्रयास"), sum(1 for r in L.ledger() if r["outcome"] == "denied"))
    s4.metric(T("Trust status", "भरोसा स्थिति"), T("Verified ✓", "सत्यापित ✓") if ok else T("Alert ⚠", "चेतावनी ⚠"))

    left, right = st.columns([3, 2])
    with left:
        st.markdown(T("#### Layer 3 · Care Moments", "#### परत 3 · केयर मोमेंट्स"))
        nxt = LK.JOURNEY[L.journey_step][0].replace("_", " ") if L.journey_step < len(LK.JOURNEY) else None
        if nxt:
            if st.button(T(f"▶ Simulate next event: {nxt}", f"▶ अगली घटना: {nxt}"), type="primary"):
                L.advance_journey()
                st.rerun()
        else:
            st.success(T("Journey complete.", "यात्रा पूरी हुई।"))
        for m in L.moments():
            icon = "🟢" if m["status"] == "delivered" else "⛔"
            st.markdown(f"{icon} **{m['ts'][11:16]}** — {m['text_hi'] if HI else m['text_en']}")
        st.markdown(T("#### Layer 2 · Access log (plain language)", "#### परत 2 · एक्सेस लॉग"))
        st.dataframe(pd.DataFrame(L.plain_language_log("hi" if HI else "en")), hide_index=True, height=300)
    with right:
        st.markdown(T("#### Layer 2 · Who can see my data", "#### परत 2 · कौन देख सकता है"))
        for p, c in L.consents().items():
            meta = LK.PARTNERS[p]
            new = st.toggle(meta["hi" if HI else "en"], value=c["granted"], disabled=meta["required"],
                            key=f"t_{p}", help=f"purpose: {c['purpose']} · expires {c['expires']} · v{c['version']}")
            if new != c["granted"]:
                L.set_consent(p, new)
                st.rerun()
        st.caption(T("Changes apply instantly: the next access request is checked against them.",
                     "बदलाव तुरंत लागू होते हैं।"))
        st.markdown(T("#### Layer 3 · Report a concern", "#### परत 3 · शिकायत दर्ज करें"))
        with st.form("griev", clear_on_submit=True):
            cat = st.selectbox(T("What happened?", "क्या हुआ?"), LK.GRIEVANCE_CATEGORIES)
            desc = st.text_area(T("Details (optional)", "विवरण (वैकल्पिक)"), max_chars=500)
            if st.form_submit_button(T("Submit", "भेजें")):
                cid = L.raise_grievance(cat, desc)
                st.success(T(f"Registered. Case ID **{cid}** — acknowledgement within "
                             f"{LK.SLA_DAYS['ack']} days, resolution target {LK.SLA_DAYS['resolve']} days.",
                             f"दर्ज हुई। केस आईडी **{cid}**"))
        for g in L.grievances():
            st.markdown(f"**{g['case_id']}** · {g['category']} · _{g['status']}_ · due {g['resolve_due']}")

# ------------------------------------------------------------------ PARTNERS
elif role == "Care partners":
    st.subheader("Policy engine — try to access Rajesh's data as a partner")
    if not L.has_consented():
        st.warning("Rajesh has not completed the consent wizard yet (Patient view).")
        st.stop()
    c1, c2, c3 = st.columns(3)
    actor = c1.selectbox("Partner", ["doctor", "lab", "pharmacy", "insurer", "research"],
                         format_func=lambda p: LK.ACTORS[p])
    data = c2.selectbox("Data requested", list(LK.DATA_LABELS), format_func=lambda d: LK.DATA_LABELS[d][0])
    purpose = c3.selectbox("Declared purpose", ["treatment", "diagnostics", "dispensing", "claims", "research", "marketing"])
    if st.button("Request access", type="primary"):
        d = L.request_access(actor, data, purpose)
        (st.success if d.allowed else st.error)(
            f"{'ALLOWED' if d.allowed else 'DENIED'} — {d.reason}. Logged with hash `{d.entry_hash[:16]}…`")
    st.markdown("**Rules enforced:** consent granted · declared purpose matches consented purpose · data type in "
                "scope · consent not expired. Try the pharmacy asking for a lab report, or anyone declaring "
                "*marketing*.")

# ------------------------------------------------------------------ DPO
else:
    st.subheader("DPO console")
    ok, bad = L.verify_chain()
    if ok:
        st.success(f"Ledger integrity verified — {len(L.ledger())} entries, hash chain intact.")
    else:
        st.error(f"Ledger TAMPERING DETECTED at entry #{bad}. Every later entry is now untrusted; "
                 "trigger incident response (CERT-In 6 h / DPB 72 h clock).")
    led = pd.DataFrame(L.ledger())
    if not led.empty:
        st.dataframe(led[["seq", "ts", "actor_role", "action", "resource", "purpose", "outcome", "detail",
                          "prev_hash", "hash"]], hide_index=True, height=320)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Tamper demo** — edit a past row as a malicious insider would (direct DB write).")
            seq = st.number_input("Entry #", 1, int(led["seq"].max()), 1)
            if st.button("Tamper with entry"):
                L.tamper(int(seq))
                st.rerun()
        with c2:
            st.download_button("Export audit log (CSV)", led.to_csv(index=False).encode(), "audit_log.csv")
            st.caption("Rule 6 of the DPDP Rules: keep access logs ≥ 1 year. CERT-In: 180 days, in India.")
    st.markdown("#### Grievance queue")
    gs = L.grievances()
    if not gs:
        st.caption("No grievances yet — raise one from the Patient view.")
    for g in gs:
        with st.expander(f"{g['case_id']} · {g['category']} · {g['status']}"):
            for u in g["updates"]:
                st.markdown(f"- {u['ts'][:16]} · **{u['status']}** — {u['note']}")
            new = st.selectbox("Update status", ["Acknowledged", "Under investigation", "Resolved", "Closed"],
                               key=f"s_{g['case_id']}")
            note = st.text_input("Note to patient", key=f"n_{g['case_id']}")
            if st.button("Send update", key=f"b_{g['case_id']}"):
                L.update_grievance(g["case_id"], new, note or new)
                st.rerun()
    st.markdown("#### Consent change history")
    st.dataframe(pd.DataFrame(L.consent_history()), hide_index=True)
ui.footer()
