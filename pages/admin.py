# Admin command center (Priority 4)
import streamlit as st
import utils.database as db
import pandas as pd
import json
import os
def show():
    # Double-check security
    if st.session_state.get("user_role") != "Admin":
        st.error("Access Denied: Administrative privileges required.")
        return

    theme = st.session_state.get("theme", "Ethereal Silk (Light)")
    if theme == "Midnight Cosmic (Dark)":
        accent_css = """
        <style>
        :root {
            --accent: #F87171;
            --accent-light: #FCA5A5;
            --accent-dark: #991B1B;
            --accent-bg: rgba(248, 113, 113, 0.12);
            --nav-hover: rgba(248, 113, 113, 0.15);
        }
        </style>
        """
    else:
        accent_css = """
        <style>
        :root {
            --accent: #991B1B;
            --accent-light: #EF4444;
            --accent-dark: #7F1D1D;
            --accent-bg: rgba(153, 27, 27, 0.08);
            --nav-hover: rgba(153, 27, 27, 0.08);
        }
        </style>
        """
    st.markdown(accent_css, unsafe_allow_html=True)
    st.header("🛡️ Platform Administration Console")
    st.write("Manage accounts, review system prediction logs, schedule appointments, and export diagnostics.")

    # 1. Total System Statistics Cards
    all_users = db.get_all_users()
    all_preds = db.get_predictions()
    all_appts = db.get_appointments()

    doctor_count = len([u for u in all_users if u["role"] == "Doctor"])
    patient_count = len([u for u in all_users if u["role"] == "Patient"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Patient Accounts", str(patient_count))
    with c2:
        st.metric("Medical Officers Registered", str(doctor_count))
    with c3:
        st.metric("Diagnostic Predictions Logged", str(len(all_preds)))
    with c4:
        st.metric("Clinical Appointments Scheduled", str(len(all_appts)))

    st.divider()

    # Create tabs
    tab_users, tab_preds, tab_appts, tab_audit, tab_db = st.tabs([
        "👤 Account Management", 
        "📄 Diagnostic Predictions", 
        "📅 Appointments Logs", 
        "🛡️ System Audit Logs",
        "⚙️ Database Export Tools"
    ])

    with tab_users:
        st.subheader("Registered Users Directory")
        df_users = pd.DataFrame(all_users)
        if not df_users.empty:
            clean_df = df_users[["email", "role", "name", "patient_id", "age", "blood_group"]].copy()
            st.dataframe(clean_df, use_container_width=True)

            user_to_delete = st.selectbox("Select user email to terminate", clean_df["email"].tolist())
            if st.button("🔴 Terminate User Account", use_container_width=True):
                if user_to_delete == "admin@healthcare.com":
                    st.error("Cannot delete root admin account.")
                else:
                    db.delete_user(user_to_delete)
                    db.add_audit_log(st.session_state.user_email, "ADMIN_DELETE_USER", f"Terminated user: {user_to_delete}")
                    st.success(f"Account {user_to_delete} successfully removed.")
                    st.rerun()
        else:
            st.info("No registered users logged in SQLite.")

    with tab_preds:
        st.subheader("Diagnostic Screening logs")
        df_preds = pd.DataFrame(all_preds)
        if not df_preds.empty:
            clean_preds = df_preds[["id", "patient_email", "disease", "risk", "prediction", "timestamp"]].copy()
            clean_preds["risk"] = clean_preds["risk"].apply(lambda r: f"{r*100:.1f}%")
            clean_preds["prediction"] = clean_preds["prediction"].apply(lambda p: "At Risk" if p == 1 else "Normal")
            st.dataframe(clean_preds, use_container_width=True)
        else:
            st.info("No diagnostics screenings recorded.")

    with tab_appts:
        st.subheader("Clinic Appointments Schedule")
        df_appts = pd.DataFrame(all_appts)
        if not df_appts.empty:
            st.dataframe(df_appts[["id", "patient_email", "doctor_name", "date_time", "reason", "status"]], use_container_width=True)
        else:
            st.info("No clinical appointments logged.")

    with tab_audit:
        st.subheader("🛡️ Platform Audit Trails (Priority 6)")
        all_audit_logs = db.get_audit_logs()
        if not all_audit_logs:
            st.info("No system audit logs found.")
        else:
            df_audit = pd.DataFrame(all_audit_logs)
            st.dataframe(df_audit[["id", "user_email", "action", "timestamp", "details"]], use_container_width=True)

    with tab_db:
        st.subheader("Export Platform Database")
        st.write("Export entire platform operational records directly. Helpful for off-site backup storage or compliance audits.")
        
        db_file = db.DB_PATH
        if os.path.exists(db_file):
            with open(db_file, "rb") as f:
                db_bytes = f.read()
            
            # Action logged on download click
            if st.download_button(
                label="📥 Download healthcare.db File",
                data=db_bytes,
                file_name="healthcare_export.db",
                mime="application/octet-stream",
                use_container_width=True
            ):
                db.add_audit_log(st.session_state.user_email, "ADMIN_EXPORT_DB", "Downloaded raw SQLite db file.")
        else:
            st.error("Database file not found.")

        # Export predictions CSV
        if all_preds:
            csv_df = pd.DataFrame(all_preds)
            csv_data = csv_df.to_csv(index=False).encode('utf-8')
            if st.download_button(
                label="📥 Export Predictions Log as CSV",
                data=csv_data,
                file_name="predictions_log.csv",
                mime="text/csv",
                use_container_width=True
            ):
                db.add_audit_log(st.session_state.user_email, "ADMIN_EXPORT_CSV", "Exported predictions log as CSV.")
