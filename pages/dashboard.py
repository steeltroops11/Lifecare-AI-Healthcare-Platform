# Dashboard page with role-specific views, Clinical Timeline, EHR context, and Doctor Notes (Priority 1, 2, 3 & 6)
import streamlit as st
from components.cards import (
    load_css, welcome, stat_card, prediction_card, 
    doctor_metric_card, report_preview_card, 
    patient_profile_card, clinical_timeline, ehr_summary_card
)
from components.charts import (
    draw_risk_gauge,
    draw_disease_distribution,
    draw_weekly_predictions,
    draw_monthly_trends,
    draw_accuracy_overview
)
import utils.database as db
from utils.helpers import get_report_history
from datetime import datetime

def compile_patient_timeline(email):
    """Compile diagnostic predictions, appointments, and doctor notes into a chronological timeline (Priority 1)."""
    events = []
    
    # 1. Predictions
    preds = db.get_predictions(email)
    for p in preds:
        events.append({
            "timestamp": p["timestamp"],
            "icon": "🧪",
            "title": f"{p['disease']} Risk Screening Assessment",
            "description": f"Calculated risk: {p['risk']*100:.1f}%. Result: {'Positive (At Risk)' if p['prediction'] == 1 else 'Negative (Low Risk)'}."
        })
        
    # 2. Appointments
    appts = db.get_appointments(email)
    for a in appts:
        events.append({
            "timestamp": a["date_time"],
            "icon": "📅",
            "title": f"Appointment with {a['doctor_name']}",
            "description": f"Reason: {a['reason']} (Status: {a['status']})"
        })
        
    # 3. Doctor Notes (Priority 3)
    notes = db.get_doctor_notes(email)
    for n in notes:
        events.append({
            "timestamp": n["timestamp"],
            "icon": "📝",
            "title": f"Clinical Progress Note by {n['doctor_name']}",
            "description": n["note"]
        })

    # Sort events by timestamp descending
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events

def show():
    st.markdown("""
        <style>
        :root {
            --accent: var(--primary);
            --accent-light: var(--primary-light);
            --accent-dark: var(--primary-dark);
            --accent-bg: var(--nav-hover);
        }
        </style>
    """, unsafe_allow_html=True)
    load_css()

    role = st.session_state.get("user_role", "Patient")
    name = st.session_state.get("user_name", "User")
    email = st.session_state.get("user_email", "")

    welcome(name, role)
    st.write("")

    if role == "Doctor":
        # -------------------------
        # DOCTOR DASHBOARD TABS (Priority 4 & 6)
        # -------------------------
        tab_clinic, tab_appts, tab_search = st.tabs([
            "🩺 Clinical Command Center", 
            "📅 Appointments Manager", 
            "🔍 Search Patients Database"
        ])

        with tab_clinic:
            st.markdown("### 👨‍⚕️ Diagnostics Operations Overview")
            
            # Pull stats dynamically from SQLite
            all_predictions = db.get_predictions()
            all_appointments = db.get_appointments()
            
            critical_count = len([p for p in all_predictions if p["prediction"] == 1])
            pending_reports = len(all_predictions)
            today_patients = len([a for a in all_appointments if a["status"] == "Accepted"])

            # Large metrics row
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                doctor_metric_card("Active Patients", str(today_patients), "Scheduled & accepted today", "📅", "var(--primary)")
            with c2:
                doctor_metric_card("Pending Reports", str(pending_reports), "Awaiting review", "📄", "var(--info)")
            with c3:
                doctor_metric_card("Critical Cases", str(critical_count), "Requires urgent check", "⚠️", "var(--danger)")
            with c4:
                doctor_metric_card("Overall Accuracy", "96%", "ML models score average", "📊", "var(--success)")

            st.divider()

            # 🚨 Critical Patient Alerts Panel
            critical_alerts = [p for p in all_predictions if p["risk"] >= 0.70]
            if critical_alerts:
                st.markdown("""
                <div style="background:#FEF2F2;border:1.5px solid #FDA4AF;border-radius:18px;
                            padding:16px 20px;margin-bottom:20px;">
                    <h4 style="margin:0 0 10px;color:#991B1B;font-size:16px;font-weight:800;">
                        🚨 CRITICAL PATIENT RISK ALERTS (Risk ≥ 70%)
                    </h4>
                    <p style="margin:0 0 12px;color:#DC2626;font-size:13.5px;">
                        The patients listed below have exhibited high risk scores on their latest screenings. Please contact them or audit their profiles immediately.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                for alert in critical_alerts[:4]:
                    col_alert_info, col_alert_btn = st.columns([3.2, 1])
                    with col_alert_info:
                        st.markdown(f"""
                        <div style="background:white;border-radius:12px;padding:12px 16px;
                                    border-left:4px solid #EF4444;box-shadow:0 2px 8px rgba(239,68,68,0.08);margin-bottom:8px;">
                            <strong style="color:#991B1B;">{alert['disease']} ({alert['risk']*100:.1f}%)</strong> · {alert['patient_email']}<br>
                            <span style="font-size:12px;color:gray;">Screened on: {alert['timestamp']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_alert_btn:
                        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                        if st.button("🔍 Audit Dossier", key=f"alert_audit_{alert['id']}", use_container_width=True):
                            st.session_state.doctor_search_patient_box = alert["patient_email"]
                            st.success(f"Dossier query set to {alert['patient_email']}! Go to 'Search Patients Database' tab.")
                            st.rerun()
                st.divider()

            # Visual Analytics Charts Row
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("<div style='text-align:center;font-weight:600;color:var(--text, #0F3D4F);'>Disease Diagnoses Distribution</div>", unsafe_allow_html=True)
                st.plotly_chart(draw_disease_distribution(all_predictions), use_container_width=True)
            with col_chart2:
                st.markdown("<div style='text-align:center;font-weight:600;color:var(--text, #0F3D4F);'>Prediction Screening Load (7 Days)</div>", unsafe_allow_html=True)
                st.plotly_chart(draw_weekly_predictions(all_predictions), use_container_width=True)

            st.divider()

            # Split: Recent Activity & Quick Actions
            col_act, col_quick = st.columns([2, 1])

            with col_act:
                st.subheader("📜 Recent Activity Logs")
                if len(all_predictions) == 0:
                    st.info("No prediction data logged in the system.")
                else:
                    for entry in all_predictions[:5]:
                        report_preview_card(
                            f"{entry['disease']} - Patient: {entry['patient_email']}",
                            entry["risk"],
                            entry["timestamp"],
                            entry["prediction"]
                        )
                    if len(all_predictions) > 5:
                        if st.button("Browse All Records", key="doc_browse_records_btn"):
                            st.session_state.page = "Reports"
                            st.rerun()

            with col_quick:
                st.subheader("⚡ Quick Actions")
                st.markdown("""
                <div style="background:#f9f9f9;padding:20px;border-radius:18px;border:1px solid #eee;margin-bottom:12px;">
                    <p style="color:gray;font-size:14px;margin-bottom:0;">Launch screening assessment modules:</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🩺 Diabetes Screening", use_container_width=True):
                    st.session_state.page = "Diabetes"
                    st.rerun()
                if st.button("❤️ Heart Disease Screening", use_container_width=True):
                    st.session_state.page = "Heart"
                    st.rerun()
                if st.button("🧬 Kidney Disease Screening", use_container_width=True):
                    st.session_state.page = "Kidney"
                    st.rerun()
                if st.button("🏥 Readmission Prediction", use_container_width=True):
                    st.session_state.page = "Readmission"
                    st.rerun()

        with tab_appts:
            st.subheader("Clinical Appointments Request Inbox")
            doc_appts = db.get_appointments()
            pending_appts = [a for a in doc_appts if a["status"] == "Scheduled"]
            
            if not pending_appts:
                st.info("No pending clinical appointments requests found.")
            else:
                for appt in pending_appts:
                    col_info, col_act1, col_act2 = st.columns([3, 1, 1])
                    with col_info:
                        st.markdown(f"""
                        <div style="background:#FFFBEB;border-left:4px solid #F59E0B;padding:12px;border-radius:8px;">
                            <strong>Patient:</strong> {appt['patient_email']}<br/>
                            <strong>Reason:</strong> {appt['reason']}<br/>
                            <strong>Requested Time:</strong> {appt['date_time']}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_act1:
                        if st.button("Accept ✅", key=f"accept_appt_{appt['id']}", use_container_width=True):
                            db.update_appointment_status(appt["id"], "Accepted")
                            db.add_notification(appt["patient_email"], f"Your appointment for {appt['reason']} has been accepted.")
                            st.success("Appointment accepted.")
                            st.rerun()
                    with col_act2:
                        if st.button("Decline ❌", key=f"decline_appt_{appt['id']}", use_container_width=True):
                            db.update_appointment_status(appt["id"], "Declined")
                            db.add_notification(appt["patient_email"], f"Your appointment request for {appt['reason']} was declined.")
                            st.warning("Appointment request declined.")
                            st.rerun()

            st.divider()
            st.subheader("Upcoming Confirmed Schedules")
            confirmed_appts = [a for a in doc_appts if a["status"] == "Accepted"]
            if not confirmed_appts:
                st.info("No confirmed upcoming appointments scheduled.")
            else:
                for appt in confirmed_appts:
                    st.markdown(f"""
                    <div style="background:#F0FDF4;border-left:4px solid #22C55E;padding:12px;border-radius:8px;margin-bottom:8px;">
                        <strong>Confirmed:</strong> {appt['patient_email']} for {appt['reason']} at {appt['date_time']}
                    </div>
                    """, unsafe_allow_html=True)

        with tab_search:
            st.subheader("🔍 Clinical Patient Registry Lookup (Priority 6)")
            
            # Retrieve all patients
            conn = db.get_connection()
            rows = conn.execute("SELECT * FROM users WHERE role = 'Patient'").fetchall()
            conn.close()
            patients = [dict(r) for r in rows]
            
            if not patients:
                st.info("No registered patient profiles found.")
            else:
                patient_emails = [p["email"] for p in patients]
                patient_map = {p["email"]: f"{p['name']} ({p['email']})" for p in patients}
                
                search_query = st.selectbox(
                    "Select Patient Profile to Audit", 
                    patient_emails, 
                    format_func=lambda x: patient_map[x],
                    key="doctor_search_patient_box"
                )
                
                if search_query:
                    selected_pat = db.get_user(search_query)
                    db.add_audit_log(email, "PATIENT_SEARCH", f"Audited patient profile: {search_query}")
                    
                    st.divider()
                    
                    # Split search results layout
                    col_pat_dossier, col_clinical_notes = st.columns([1.2, 1])
                    
                    with col_pat_dossier:
                        st.write("### Patient Profile & EHR Dossier")
                        patient_profile_card(selected_pat)
                        ehr_summary_card(selected_pat)
                        
                        st.write("### 📈 Patient Bio-Marker Vital Trends")
                        pat_preds = db.get_predictions(search_query)
                        from components.charts import draw_biomarker_trends
                        st.plotly_chart(draw_biomarker_trends(pat_preds), use_container_width=True)
                        
                        st.write("### 🕒 Patient Clinical Timeline")
                        events = compile_patient_timeline(search_query)
                        clinical_timeline(events)
                        
                    with col_clinical_notes:
                        st.write("### 📝 Add Physician Progress Note (Priority 3)")
                        with st.form("add_physician_note_form", clear_on_submit=True):
                            note_text = st.text_area("Enter Progress/Treatment Note", placeholder="Patient status improving. Continue medication...")
                            note_submitted = st.form_submit_button("💾 Save Progress Note", use_container_width=True)
                            
                            if note_submitted:
                                if not note_text.strip():
                                    st.error("Please enter note content.")
                                else:
                                    db.create_doctor_note(search_query, name, note_text)
                                    db.add_notification(search_query, f"Dr. {name} has appended a new clinical progress note to your chart.")
                                    st.success("Note saved successfully!")
                                    st.rerun()
                                    
                        st.write("#### Historical Clinical Notes")
                        h_notes = db.get_doctor_notes(search_query)
                        if not h_notes:
                            st.info("No notes recorded for this patient.")
                        else:
                            for hn in h_notes:
                                st.markdown(f"""
                                <div style="background:#F9FBFB;border-left:3px solid #7B8E96;padding:12px;border-radius:8px;margin-bottom:8px;">
                                    <span style="font-size:11px;color:gray;">{hn['timestamp']} | Writer: {hn['doctor_name']}</span>
                                    <p style="margin:4px 0 0;font-size:14px;color:#0F3D4F;">{hn['note']}</p>
                                </div>
                                """, unsafe_allow_html=True)

    else:
        # -------------------------
        # PATIENT DASHBOARD (Priority 1, 2)
        # -------------------------
        patient_predictions = db.get_predictions(email)
        critical_personal = len([p for p in patient_predictions if p["prediction"] == 1])
        appointments_personal = db.get_appointments(email)

        # Personal metrics row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            stat_card("Appointments Scheduled", str(len(appointments_personal)), icon="📅", color="#0F6E84")
        with c2:
            stat_card("Reports Logged", str(len(patient_predictions)), icon="📄", color="#1AA7C8")
        with c3:
            stat_card("Critical Alerts", str(critical_personal), icon="⚠️", color="#EF4444")
        with c4:
            stat_card("Overall Accuracy", "96%", icon="📊", color="#22C55E")

        st.divider()

        # Upcoming Appointment Alert Banner (M5)
        upcoming_appts = [a for a in appointments_personal if a["status"] in ["Scheduled", "Accepted"]]
        if upcoming_appts:
            next_appt = upcoming_appts[0]
            st.markdown(f"""
            <div style="background:#ECFDF5;border:1.5px solid #10B98130;border-left:4px solid #10B981;
                        border-radius:14px;padding:14px 18px;margin-bottom:18px;">
                <h4 style="margin:0;color:#065F46;font-size:15px;font-weight:800;">
                    📅 Upcoming Appointment Alert
                </h4>
                <p style="margin:4px 0 0;color:#047857;font-size:13.5px;">
                    You have a confirmed consult scheduled for <strong>{next_appt['reason']}</strong> with <strong>{next_appt['doctor_name']}</strong> at <strong>{next_appt['date_time']}</strong>.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Split: Left (Gauges), Right (Book Appointment Form)
        col_g, col_book = st.columns([1.2, 1])

        with col_g:
            if patient_predictions:
                st.subheader("🎯 Active Diagnosis Risk Dial")
                latest_p = patient_predictions[0]
                st.plotly_chart(draw_risk_gauge(latest_p["risk"] * 100, f"Latest Screening: {latest_p['disease']}"), use_container_width=True)
                
                st.subheader("📈 My Vital Trends Tracker")
                from components.charts import draw_biomarker_trends
                st.plotly_chart(draw_biomarker_trends(patient_predictions), use_container_width=True)
            else:
                st.info("Perform a diagnostic prediction screening to view dials visualization here.")
                st.plotly_chart(draw_accuracy_overview(), use_container_width=True)

        with col_book:
            st.subheader("📅 Book Clinic Appointment (Priority 2)")
            
            with st.form("book_appt_form"):
                doctor_name = st.selectbox("Select Doctor specialty", [
                    "Dr. Navish (Endocrinology)", 
                    "Dr. Sarah Jenkins (Nephrology)", 
                    "Dr. Marcus Vance (Cardiology)"
                ])
                appt_date = st.date_input("Select Appointment Date")
                appt_time = st.selectbox("Select Appointment Time", [
                    "09:00 AM", "10:00 AM", "11:00 AM", 
                    "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"
                ])
                reason = st.text_input("Consultation Reason", placeholder="e.g. Heart screening checkup follow-up")
                
                submitted = st.form_submit_button("Book Appointment Request", use_container_width=True)
                
                if submitted:
                    if not reason.strip():
                        st.error("Please enter a valid consultation reason.")
                    else:
                        date_time_str = f"{appt_date} {appt_time}"
                        db.create_appointment(email, doctor_name, date_time_str, reason)
                        
                        db.add_notification(email, f"Appointment requested with {doctor_name} for '{reason}' at {date_time_str}.")
                        db.add_notification("doctor@healthcare.com", f"New appointment request from patient {email} for '{reason}'.")
                        
                        st.success(f"Appointment request with {doctor_name} submitted successfully!")
                        st.rerun()

        # Phase 4 — Specialist Finder Quick-Action Card
        st.divider()
        col_spec, col_reminders = st.columns(2)

        with col_spec:
            st.subheader("🔍 Find a Specialist")
            # Show last prediction risk tier if available
            if patient_predictions:
                lp = patient_predictions[0]
                from utils.recommendation_engine import _get_risk_tier
                tier = _get_risk_tier(lp['risk'] * 100)
                st.markdown(f"""
                <div style="background:{tier['risk_bg']};border:1.5px solid {tier['risk_color']}40;
                            border-radius:14px;padding:14px 18px;margin-bottom:12px;">
                    <span style="font-size:20px;">{tier['risk_emoji']}</span>
                    <strong style="color:#0F3D4F;"> Last Screening: {lp['disease']}</strong>
                    <p style="margin:4px 0 0;color:{tier['risk_color']};font-size:14px;font-weight:600;">
                        Risk: {lp['risk']*100:.1f}% &nbsp;&middot;&nbsp; {tier['risk_level']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            if st.button("🏥 Find Nearby Specialist", use_container_width=True, key="dash_find_specialist"):
                st.session_state.page = "Specialist Finder"
                st.rerun()

        with col_reminders:
            st.subheader("💊 My Health Reminders")
            try:
                reminders = db.get_followups(email, status='pending')
                if reminders:
                    for rem in reminders[:4]:
                        icon_map = {"medicine":"💊","exercise":"🏃","water":"💧","test":"🔬","consultation":"📅"}
                        icon = icon_map.get(rem['reminder_type'], "🔔")
                        col_rem_info, col_rem_done = st.columns([3, 1])
                        with col_rem_info:
                            st.markdown(f"""
                            <div style="background:#F0F9FF;border-left:3px solid #38BDF8;
                                        padding:10px 14px;border-radius:8px;margin-bottom:6px;">
                                <strong>{icon} {rem['message']}</strong><br>
                                <span style="font-size:12px;color:gray;">Due: {rem['due_date']} &middot; {rem['disease']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_rem_done:
                            if st.button("✅", key=f"done_rem_{rem['id']}", help="Mark done"):
                                db.update_followup_status(rem['id'], 'done')
                                st.rerun()
                else:
                    st.info("No pending reminders. Set one from a disease screening page.")
            except Exception:
                st.info("Health reminders will appear here after running a disease screening.")

            # Medication Schedule Tracker (Priority 2)
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("💊 Active Medications & Schedule")
            user_data = db.get_user(email)
            meds_str = user_data.get("medications", "") if user_data else ""
            if meds_str and meds_str.lower() != "none" and meds_str.strip():
                meds_list = [m.strip() for m in meds_str.split(",") if m.strip()]
                for idx, med in enumerate(meds_list):
                    slots = ["08:00 AM - Breakfast", "01:00 PM - Lunch", "09:00 PM - Dinner"]
                    slot = slots[idx % len(slots)]
                    st.markdown(f"""
                    <div style="background:#FFFDF5;border-left:3px solid #F59E0B;
                                padding:10px 14px;border-radius:8px;margin-bottom:6px;display:flex;justify-content:space-between;">
                        <div>
                            <strong>{med}</strong><br>
                            <span style="font-size:12px;color:gray;">🕒 {slot}</span>
                        </div>
                        <span style="background:#FFF9E6;color:#D97706;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;height:fit-content;">Active</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active medications found in your profile. Update them in your Profile page to generate daily schedule slots.")

        # Prediction Modules Grid
        st.divider()
        st.subheader("🛠️ Screening Modules")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            prediction_card("🩺", "Diabetes Checkup", "Predict diabetes risk factors")
            if st.button("Open Diabetes Module", use_container_width=True):
                st.session_state.page = "Diabetes"
                st.rerun()
        with col_m2:
            prediction_card("❤️", "Heart Checkup", "Predict cardiovascular risk factors")
            if st.button("Open Heart Module", use_container_width=True):
                st.session_state.page = "Heart"
                st.rerun()

        col_m3, col_m4 = st.columns(2)
        with col_m3:
            prediction_card("🧬", "Kidney Checkup", "Predict kidney function concerns")
            if st.button("Open Kidney Module", use_container_width=True):
                st.session_state.page = "Kidney"
                st.rerun()
        with col_m4:
            prediction_card("🏥", "Readmission Checkup", "Evaluate hospital readmission chances")
            if st.button("Open Readmission Module", use_container_width=True):
                st.session_state.page = "Readmission"
                st.rerun()

        # Tabs for History Reports vs Clinical Timeline
        st.divider()
        tab_journal, tab_timeline = st.tabs(["📋 Recent Personal Health Reports", "🕒 Clinical History Timeline (Priority 1)"])
        
        with tab_journal:
            if len(patient_predictions) == 0:
                st.info("No prediction reports found for your account.")
            else:
                for entry in patient_predictions[:5]:
                    report_preview_card(
                        entry["disease"],
                        entry["risk"],
                        entry["timestamp"],
                        entry["prediction"]
                    )
                if len(patient_predictions) > 5:
                    if st.button("View Full Health Journal", key="pat_view_journal_btn"):
                        st.session_state.page = "Reports"
                        st.rerun()
                        
        with tab_timeline:
            st.write("### Chronological Clinical History Timeline")
            pat_timeline = compile_patient_timeline(email)
            clinical_timeline(pat_timeline)