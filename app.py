import streamlit as st

# Globally disable Streamlit's automatic Plotly theme override to preserve custom CSS colors
_orig_plotly_chart = st.plotly_chart
def _custom_plotly_chart(*args, **kwargs):
    if "theme" not in kwargs:
        kwargs["theme"] = None
    return _orig_plotly_chart(*args, **kwargs)
st.plotly_chart = _custom_plotly_chart

from utils.auth import init_session, check_auth, logout
from utils.helpers import get_models
from components.styles import load_app_css
from components.navbar import render_topbar, render_nav_buttons

# Import pages
from pages import dashboard, diabetes, heart, kidney, readmission, reports, profile, chat, admin, settings
from pages import specialist_finder

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="Healthcare Analytics System",
    page_icon="🏥",
    layout="wide"
)

# 2. Session Initialization
init_session()

# 3. Model Loading & Caching
get_models()

# 4. Global CSS Styles Injection
load_app_css()

# 5. Authentication Verification Guard
if check_auth():
    # 6. Global Top Navigation Header
    render_topbar()

    # 7. Navigation Options Bar
    render_nav_buttons()

    # 8. Sidebar Styled Profile Panel & Logout Control
    with st.sidebar:
        user_initial = (st.session_state.user_name or "U")[0].upper()
        st.markdown(f"""
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{user_initial}</div>
            <p class="sidebar-name">{st.session_state.user_name}</p>
            <p class="sidebar-email">{st.session_state.user_email}</p>
            <span class="sidebar-role-badge">{st.session_state.user_role}</span>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    # 9. Page Router Definition
    page_routes = {
        "Dashboard": dashboard.show,
        "Diabetes": diabetes.show,
        "Heart": heart.show,
        "Kidney": kidney.show,
        "Readmission": readmission.show,
        "Reports": reports.show,
        "Profile": profile.show,
        "Chat AI": chat.show,
        "Admin Panel": admin.show,
        "Settings": settings.show,
        "Specialist Finder": specialist_finder.show,
    }

    # 10. Page transition animation (only on actual navigation, not on
    #     in-page widget interactions).
    _prev_page = st.session_state.get("_prev_page")
    _current_page = st.session_state.get("page", "Dashboard")
    if _prev_page is not None and _prev_page != _current_page:
        st.markdown(
            "<style>"
            ".block-container{animation:pageFadeIn .45s cubic-bezier(.22,1,.36,1);}"
            ".block-container > .element-container{animation:slideUp .5s cubic-bezier(.22,1,.36,1) both;}"
            "</style>",
            unsafe_allow_html=True,
        )
    st.session_state["_prev_page"] = _current_page

    # 11. Execute Routed Page (Priority Safe Fallback Router)
    page_routes.get(_current_page, dashboard.show)()