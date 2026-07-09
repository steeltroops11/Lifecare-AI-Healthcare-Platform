# Authentication utilities with SQLite backend
import streamlit as st
from urllib.parse import unquote
import os
import utils.database as db
from utils.logger import get_logger

logger = get_logger("utils.auth")
LOGIN_URL = os.getenv("LOGIN_URL", "http://localhost:5000")

def init_session():
    """Initialize all session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "reports" not in st.session_state:
        st.session_state["reports"] = {}
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

def check_auth():
    """Parse URL auth params, sync with SQLite, and handle login redirect."""
    query_params = st.query_params

    if query_params.get("auth") == "1" and not st.session_state.logged_in:
        email = query_params.get("email", "")
        role = query_params.get("role", "Patient")
        name = unquote(query_params.get("name", "User"))

        logger.info(f"[AUTH_INIT] email='{email}' role='{role}' name='{name}'")

        # Fetch user or create if not present (e.g. Google Login Simulator)
        user_info = db.get_user(email)
        if not user_info:
            db.create_user(email, "social_login_no_password", role, name)
            user_info = db.get_user(email)

        st.session_state.logged_in = True
        st.session_state.user_role = user_info["role"]
        st.session_state.user_email = user_info["email"]
        st.session_state.user_name = user_info["name"]
        
        # Populate session state report cache from database prediction log
        st.session_state["reports"] = {}
        predictions = db.get_predictions(user_info["email"])
        for p in predictions:
            # Keep latest prediction per disease for dashboard compatibility
            if p["disease"] not in st.session_state["reports"]:
                st.session_state["reports"][p["disease"]] = {
                    "prediction": p["prediction"],
                    "risk": p["risk"]
                }

        st.query_params.clear()
        st.rerun()

    if not st.session_state.logged_in:
        logger.info("[AUTH_REDIRECT] status='unauthenticated'")
        from pages import landing
        landing.show()
        
        # Admin / developer credentials help drawer at the footer of landing page
        with st.expander("🛠️ Developer Credentials & Direct Portal Links"):
            st.markdown("""
                <div style="padding: 10px; border-radius: 8px; border: 1px dashed #ccc; margin-bottom:10px;">
                     <p style="margin:0;font-size:14px;color:gray;">
                        If you need to login directly or simulate Google Login, use the link below:
                        <a href="http://localhost:5000" target="_self" style="color:#0F6E84; font-weight:700; text-decoration:none;">
                            Direct Portal Link (http://localhost:5000)
                        </a>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.code("Admin Login: admin@healthcare.com / admin123\nDoctor Login: doctor@healthcare.com / doctor123\nPatient Login: patient@healthcare.com / patient123")
        st.stop()

    return True

def logout():
    """Clear session state and logout."""
    email = st.session_state.get("user_email")
    logger.info(f"[AUTH_LOGOUT] email='{email}'")
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state["reports"] = {}
    st.session_state.page = "Dashboard"
    st.query_params.clear()
    st.rerun()
