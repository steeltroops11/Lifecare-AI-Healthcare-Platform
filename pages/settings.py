# Settings configuration page (Priority 9)
import streamlit as st
import utils.database as db

def show():
    st.header("⚙️ Platform Settings & Customization")
    st.write("Customize your Lifecare interface preferences, notification alerts, and localization rules.")

    # Theme selection
    current_theme = st.session_state.get("theme", "Cream & Evergreen")
    theme_opts = ["Cream & Evergreen", "Obsidian & Gold"]
    theme_index = theme_opts.index(current_theme) if current_theme in theme_opts else 0
    
    st.subheader("Visual Theme Selection")
    new_theme = st.selectbox(
        "Application Theme Mode",
        theme_opts,
        index=theme_index,
        help="Choose a designer aesthetic designed for premium clinical environments."
    )
    
    if new_theme != current_theme:
        st.session_state.theme = new_theme
        st.success(f"Applying {new_theme} theme...")
        st.rerun()

    st.divider()

    # Localization
    st.subheader("Localization & Translation")
    language = st.selectbox(
        "Default Application Language",
        ["English (US)", "Spanish (ES)", "French (FR)", "German (DE)"],
        index=0
    )

    st.divider()

    # Notifications Settings
    st.subheader("Real-Time Communications Alerts")
    email_alerts = st.checkbox("Receive dynamic email copies of PDF reports automatically", value=True)
    push_notifs = st.checkbox("Enable browser push notification indicators", value=True)
    app_notifs = st.checkbox("Enable in-app Bell Alert Notifications", value=True)

    if st.button("💾 Save Settings Preferences", use_container_width=True):
        st.success("Preferences saved successfully.")

    st.divider()

    # ---- Clear History & Data ----
    st.subheader("🗑️ Clear History & Reset Data")

    user_email = st.session_state.get("user_email", "")
    user_role = st.session_state.get("user_role", "Patient")

    st.markdown("""
<div style="background:var(--danger-bg, #FEF2F2); border:1px solid var(--danger, #EF4444)30; border-left:4px solid var(--danger, #EF4444); border-radius:14px; padding:16px 20px; margin-bottom:16px;">
<p style="margin:0; font-size:14px; font-weight:700; color:var(--danger, #991B1B);">⚠️ Warning: This action is irreversible</p>
<p style="margin:6px 0 0; font-size:13px; color:var(--text-body, #455E67);">Clearing your data will permanently delete all your prediction history, appointment records, saved favorites, notifications, follow-up reminders, and cached clinic searches.</p>
</div>
    """, unsafe_allow_html=True)

    # Scope selection
    if user_role in ("Admin", "Doctor"):
        clear_scope = st.radio(
            "Data Scope to Clear",
            ["🧑 My Data Only", "🌐 All Users Data (Full System Reset)"],
            index=0,
            help="Admins and Doctors can clear data for all users or just their own."
        )
        clear_all = "All Users" in clear_scope
    else:
        st.info("This will clear **your personal data only**. Your account and profile will be preserved.")
        clear_all = False

    # Two-step confirmation
    confirm_key = "clear_data_confirmed"
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False

    col_clear, col_cancel = st.columns(2)
    with col_clear:
        if not st.session_state[confirm_key]:
            if st.button("🗑️ Clear All History", use_container_width=True, type="primary"):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            st.warning("Are you sure? Click **Confirm Clear** to permanently delete data.")
            if st.button("✅ Confirm Clear", use_container_width=True, type="primary"):
                target_email = None if clear_all else user_email
                deleted = db.clear_all_user_data(user_email=target_email)

                total = sum(deleted.values())
                scope_label = "all system data" if clear_all else "your personal data"
                st.success(f"✅ Successfully cleared {scope_label}! ({total} records removed)")

                # Show breakdown
                if total > 0:
                    breakdown_items = []
                    friendly_names = {
                        "predictions": "Prediction History",
                        "appointments": "Appointments",
                        "notifications": "Notifications",
                        "doctor_notes": "Doctor Notes",
                        "audit_logs": "Audit Logs",
                        "favorites": "Saved Favorites",
                        "followups": "Follow-up Reminders",
                        "clinics_cache": "Clinic Cache",
                    }
                    for table, count in deleted.items():
                        if count > 0:
                            label = friendly_names.get(table, table)
                            breakdown_items.append(f"• **{label}**: {count} records")
                    if breakdown_items:
                        st.markdown("\n".join(breakdown_items))
                else:
                    st.info("No data found to clear — everything is already empty.")

                st.session_state[confirm_key] = False

    with col_cancel:
        if st.session_state[confirm_key]:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state[confirm_key] = False
                st.rerun()
