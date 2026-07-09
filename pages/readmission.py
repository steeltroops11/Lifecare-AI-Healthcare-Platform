# Readmission prediction page with clinical flow, Plotly gauges, and Phase 4 AI Recommendation System
import streamlit as st
from components.cards import custom_metric_card, result_card, patient_profile_card, ai_recommendation_panel, followup_reminder_form, prediction_confidence_row
from components.charts import draw_risk_gauge, draw_xai_feature_contributions
from utils.helpers import get_models, save_to_history, get_model_info
import utils.database as db
from utils.pdf_generator import recommendations, generate_single_report_pdf
from utils.recommendation_engine import get_recommendation

def show():
    st.header("🏥 Hospital Readmission Risk Prediction")

    # ---- 1. Patient Selection / Info ----
    st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
    
    role = st.session_state.get("user_role", "Patient")
    
    if role == "Doctor":
        conn = db.get_connection()
        rows = conn.execute("SELECT * FROM users WHERE role = 'Patient'").fetchall()
        conn.close()
        patients = [dict(r) for r in rows]
        
        patient_options = {p["email"]: f"{p['name']} ({p['email']})" for p in patients}
        selected_patient_email = st.selectbox("Select Patient to Screen", list(patient_options.keys()), format_func=lambda x: patient_options[x], key="readm_patient_select")
        patient_data = db.get_user(selected_patient_email)
    else:
        patient_data = db.get_user(st.session_state.get("user_email"))

    if patient_data:
        patient_profile_card(patient_data)
    else:
        st.warning("Patient profile details could not be loaded.")

    # ---- 2. Clinical Inputs ----
    st.markdown('<div class="section-header">🔬 Clinical Information Inputs</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        time_in_hospital = st.number_input("Time in Hospital (days)", 1, 14, 4, key="readm_time")
        num_lab_procedures = st.number_input("Number of Lab Procedures", 0, 150, 40, key="readm_lab")
        num_procedures = st.number_input("Number of Procedures", 0, 10, 1, key="readm_proc")
        num_medications = st.number_input("Number of Medications", 0, 100, 15, key="readm_meds")

    with col2:
        number_outpatient = st.number_input("Outpatient Visits (past year)", 0, 50, 0, key="readm_out")
        number_emergency = st.number_input("Emergency Visits (past year)", 0, 50, 0, key="readm_emg")
        number_inpatient = st.number_input("Inpatient Visits (past year)", 0, 50, 0, key="readm_in")
        number_diagnoses = st.number_input("Number of Diagnoses", 1, 20, 7, key="readm_diag")

    # ---- 3. Predict Button ----
    st.markdown("---")
    if st.button("🔮 Calculate Readmission Risk", key="predict_readmission", use_container_width=True):
        models = get_models()
        readmission_defaults = models["readmission_defaults"]
        readmission_model = models["readmission"]

        row = readmission_defaults["defaults"].copy()
        row["time_in_hospital"] = time_in_hospital
        row["num_lab_procedures"] = num_lab_procedures
        row["num_procedures"] = num_procedures
        row["num_medications"] = num_medications
        row["number_outpatient"] = number_outpatient
        row["number_emergency"] = number_emergency
        row["number_inpatient"] = number_inpatient
        row["number_diagnoses"] = number_diagnoses

        features = [[row[col] for col in readmission_defaults["columns"]]]

        prediction = readmission_model.predict(features)[0]
        probability = readmission_model.predict_proba(features)[0][1]

        # Save to database
        save_to_history("Readmission", prediction, probability, {
            "time_in_hospital": time_in_hospital, "num_lab_procedures": num_lab_procedures,
            "num_procedures": num_procedures, "num_medications": num_medications,
            "number_outpatient": number_outpatient, "number_emergency": number_emergency,
            "number_inpatient": number_inpatient, "number_diagnoses": number_diagnoses
        })

        # Save prediction results locally in session
        st.session_state[f"last_pred_readm_{patient_data['email']}"] = {
            "risk": probability,
            "prediction": prediction,
            "inputs": {
                "time_in_hospital": time_in_hospital, "num_lab_procedures": num_lab_procedures,
                "num_procedures": num_procedures, "num_medications": num_medications,
                "number_outpatient": number_outpatient, "number_emergency": number_emergency,
                "number_inpatient": number_inpatient, "number_diagnoses": number_diagnoses
            }
        }
        st.rerun()

    # Retrieve last prediction from session
    last_pred_key = f"last_pred_readm_{patient_data['email']}"
    if last_pred_key in st.session_state:
        pred_res = st.session_state[last_pred_key]
        prob = pred_res["risk"]
        pred = pred_res["prediction"]

        # ---- 4. Risk Card & Gauge ----
        st.markdown('<div class="section-header">📊 Risk Assessment Results</div>', unsafe_allow_html=True)
        
        col_res1, col_res2, col_res3 = st.columns([1, 1, 1.2])
        with col_res1:
            if pred == 1:
                result_card("error", "High Readmission Risk Detected", 
                            "The predictive model indicates high risk of readmission within 30 days of discharge.")
            else:
                result_card("success", "Low Readmission Risk Detected", 
                            "The predictive model indicates a low chance of readmission within 30 days.")
            
            custom_metric_card("Readmission Probability", f"{prob*100:.2f}%", "#EF4444" if pred == 1 else "#22C55E")
        
        with col_res2:
            st.plotly_chart(draw_risk_gauge(prob * 100, "Readmission Risk Dial"), use_container_width=True)

        with col_res3:
            st.plotly_chart(draw_xai_feature_contributions("Readmission", pred_res["inputs"]), use_container_width=True)

        # ---- 5. Phase 4 AI Recommendation Panel ----
        patient_data_full = db.get_user(patient_data['email']) or patient_data
        rec_obj = get_recommendation("Readmission", prob, patient_data_full, pred_res["inputs"])

        if rec_obj.get("emergency"):
            st.session_state["specialist_disease"]   = "Readmission"
            st.session_state["specialist_risk"]       = prob
            st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
            st.session_state["specialist_type"]       = rec_obj["specialist"]
            st.session_state["specialist_emergency"]  = True
            st.session_state["specialist_rec_obj"]    = rec_obj

        # Confidence display row (Phase 4 M6/EX-1)
        model_info = get_model_info("Readmission", prob)
        prediction_confidence_row(
            risk_pct=prob * 100,
            confidence_pct=model_info["confidence_pct"],
            model_name=model_info["model_name"]
        )

        ai_recommendation_panel(
            "Readmission", prob,
            rec_obj.get("explanation", ""),
            recommendations["Readmission"],
            rec_obj.get("department", "Internal Medicine & Care Transitions"),
            rec_obj=rec_obj
        )

        col_find, col_remind = st.columns(2)
        with col_find:
            if st.button("🏥 Find Nearby Care Coordinators", key="find_coord_btn", use_container_width=True):
                st.session_state["specialist_disease"]   = "Readmission"
                st.session_state["specialist_risk"]       = prob
                st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
                st.session_state["specialist_type"]       = "General Physician"
                st.session_state["specialist_emergency"]  = rec_obj.get("emergency", False)
                st.session_state["specialist_rec_obj"]    = rec_obj
                st.session_state.page = "Specialist Finder"
                st.rerun()
        with col_remind:
            if rec_obj["risk_level"] in ["HIGH", "CRITICAL"]:
                if st.button("💊 Set Health Reminder", key="readm_reminder_toggle", use_container_width=True):
                    st.session_state["show_readm_reminder"] = not st.session_state.get("show_readm_reminder", False)
        if st.session_state.get("show_readm_reminder"):
            followup_reminder_form("Readmission")

        # ---- 6. Download ----
        st.markdown('<div class="section-header">📄 Official Clinical Report</div>', unsafe_allow_html=True)
        
        pdf_path = generate_single_report_pdf(
            "Readmission", prob, pred, recommendations["Readmission"]
        )
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Readmission Report PDF",
                data=f,
                file_name=f"Readmission_Report_{patient_data['name'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        if st.button("✉️ Email Report PDF to Registered Address", key="email_report_readm", use_container_width=True):
            st.success(f"Clinical report PDF successfully dispatched to: {patient_data['email']} (Simulated)")
            db.add_notification(patient_data['email'], "Copy of your Hospital Readmission Risk Screening Report PDF has been emailed to you.")
