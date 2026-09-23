"""My Health Data Locker — Digital Trust Toolkit (Streamlit entry point).

Run locally:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Health Data Locker · Digital Trust Toolkit", page_icon="🔐",
                   layout="wide", initial_sidebar_state="expanded")

pages = {
    "Case": [
        st.Page("app_pages/home.py", title="Overview", icon="🏠", default=True),
        st.Page("app_pages/strategy.py", title="Strategy & ESG", icon="🧭"),
    ],
    "Evidence": [
        st.Page("app_pages/research_lab.py", title="Research Lab", icon="📊"),
        st.Page("app_pages/kano.py", title="Kano Analyzer", icon="🎯"),
    ],
    "Solution": [
        st.Page("app_pages/locker.py", title="Locker Prototype", icon="🔐"),
        st.Page("app_pages/security.py", title="Security Architecture", icon="🛡️"),
    ],
    "Decision tools": [
        st.Page("app_pages/dpdp.py", title="DPDP Readiness", icon="✅"),
        st.Page("app_pages/roi.py", title="ROI Simulator", icon="💹"),
    ],
}
st.navigation(pages).run()
