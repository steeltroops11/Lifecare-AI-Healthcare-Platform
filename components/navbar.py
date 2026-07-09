# Navbar component with notification alerts and dynamic routing (Priority 3 & 4)
import streamlit as st
from utils.auth import logout
import utils.database as db

def render_topbar():
    """Render the top navigation bar with dynamic notifications count (Priority 3)."""
    user_email = st.session_state.get("user_email", "")
    user_name = st.session_state.get("user_name", "User")
    user_role = st.session_state.get("user_role", "Patient")

    # Get notifications from SQLite
    notifications_count = 0
    if user_email:
        try:
            notifs = db.get_notifications(user_email)
            notifications_count = len([n for n in notifs if n["read"] == 0])
        except Exception:
            pass

    # Bell icon text
    bell_text = f"🔔 ({notifications_count})" if notifications_count > 0 else "🔔"

    st.markdown(f"""
    <div class="top-navbar">
        <div class="nav-brand">🏥 Lifecare Clinical Platform</div>
        <div class="nav-links">
            <span class="nav-link" id="nav-notifs" style="position:relative;cursor:pointer;font-weight:700;">{bell_text}</span>
            <span class="nav-link">👤 {user_name}</span>
            <span class="nav-link" style="color:#0F6E84;font-weight:700;background:#0F6E8410;padding:4px 10px;border-radius:6px;">{user_role}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit notification drop-down expander below the topbar
    if notifications_count > 0:
        with st.expander("📬 System Notifications Inbox"):
            notifs = db.get_notifications(user_email)
            for n in notifs[:5]:
                read_badge = "🟢" if n["read"] == 0 else "⚪"
                st.write(f"{read_badge} **{n['timestamp']}**: {n['message']}")
            if st.button("Mark All as Read", key="read_all_notifs_btn"):
                db.mark_notifications_as_read(user_email)
                st.rerun()

def render_nav_buttons():
    """Render dynamic navigation bar with native Streamlit buttons styled beautifully."""
    role = st.session_state.get("user_role", "Patient")
    current_page = st.session_state.get("page", "Dashboard")
    
    # Define pages available by role with icons
    page_config = [
        ("Dashboard",         "🏠"),
        ("Diabetes",          "🩺"),
        ("Heart",             "❤️"),
        ("Kidney",            "🧬"),
        ("Readmission",       "🏥"),
        ("Reports",           "📄"),
        ("Specialist Finder", "🔍"),
    ]
    
    if role == "Patient":
        page_config.append(("Chat AI", "🤖"))
    
    if role == "Admin":
        page_config.append(("Admin Panel", "🛡️"))
        
    page_config.append(("Settings", "⚙️"))

    # Render container marker for CSS targeting
    st.markdown('<div id="nav-container-marker"></div>', unsafe_allow_html=True)

    # Render buttons in horizontal columns
    cols = st.columns(len(page_config))
    for idx, (page_name, icon) in enumerate(page_config):
        with cols[idx]:
            is_active = (current_page == page_name)
            btn_type = "primary" if is_active else "secondary"
            label = f"{icon} {page_name}"
            
            if st.button(label, key=f"nav_btn_real_{page_name}", type=btn_type):
                st.session_state.page = page_name
                st.rerun()
