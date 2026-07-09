# Heart disease prediction page with clinical flow, Plotly gauges, and Phase 4 AI Recommendation System
import streamlit as st
from components.cards import custom_metric_card, result_card, patient_profile_card, ai_recommendation_panel, followup_reminder_form, prediction_confidence_row
from components.charts import draw_risk_gauge, draw_xai_feature_contributions
from utils.helpers import get_models, save_to_history, get_model_info
import utils.database as db
from utils.pdf_generator import recommendations, generate_single_report_pdf
from utils.recommendation_engine import get_recommendation

def show():
    st.header("❤️ Cardiovascular Disease Risk Screening")

    # ---- 1. Patient Selection / Info ----
    st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
    
    role = st.session_state.get("user_role", "Patient")
    
    if role == "Doctor":
        conn = db.get_connection()
        rows = conn.execute("SELECT * FROM users WHERE role = 'Patient'").fetchall()
        conn.close()
        patients = [dict(r) for r in rows]
        
        patient_options = {p["email"]: f"{p['name']} ({p['email']})" for p in patients}
        selected_patient_email = st.selectbox("Select Patient to Screen", list(patient_options.keys()), format_func=lambda x: patient_options[x], key="heart_patient_select")
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
        age = st.number_input("Age", min_value=1, max_value=120, value=50, key="heart_age")
        sex = st.selectbox("Sex", ["Female", "Male"], key="heart_sex")
        cp = st.selectbox("Chest Pain Type (cp) [0: Typical, 1: Atypical, 2: Non-anginal, 3: Asymptomatic]", [0, 1, 2, 3], key="heart_cp")
        trestbps = st.number_input("Resting Blood Pressure (mm Hg)", min_value=80, max_value=250, value=120, key="heart_bp")
        chol = st.number_input("Serum Cholestoral (mg/dl)", min_value=100, max_value=700, value=200, key="heart_chol")
        fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl (0: False, 1: True)", [0, 1], key="heart_fbs")
        restecg = st.selectbox("Resting Electrocardiographic Results (restecg)", [0, 1, 2], key="heart_restecg")

    with col2:
        thalach = st.number_input("Maximum Heart Rate Achieved", min_value=50, max_value=250, value=150, key="heart_thalach")
        exang = st.selectbox("Exercise Induced Angina (exang) (0: No, 1: Yes)", [0, 1], key="heart_exang")
        oldpeak = st.number_input("ST Depression Induced by Exercise (oldpeak)", min_value=0.0, max_value=10.0, value=1.0, step=0.1, key="heart_oldpeak")
        slope = st.selectbox("Slope of the Peak Exercise ST Segment (slope)", [0, 1, 2], key="heart_slope")
        ca = st.selectbox("Number of Major Vessels Colored by Flourosopy (ca)", [0, 1, 2, 3, 4], key="heart_ca")
        thal = st.selectbox("Thal (0: Normal, 1: Fixed Defect, 2: Reversible Defect)", [0, 1, 2, 3], key="heart_thal")

    sex_value = 1 if sex == "Male" else 0

    # ---- 3. Predict Button ----
    st.markdown("---")
    if st.button("🔮 Calculate Cardiovascular Risk", key="predict_heart", use_container_width=True):
        models = get_models()
        features = [[age, sex_value, cp, trestbps, chol, fbs, restecg,
                      thalach, exang, oldpeak, slope, ca, thal]]

        prediction = models["heart"].predict(features)[0]
        probability = models["heart"].predict_proba(features)[0][1]

        # Save to database
        save_to_history("Heart Disease", prediction, probability, {
            "age": age, "sex": sex_value, "cp": cp, "trestbps": trestbps, "chol": chol,
            "fbs": fbs, "restecg": restecg, "thalach": thalach, "exang": exang,
            "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal
        })

        # Save prediction results locally in session
        st.session_state[f"last_pred_heart_{patient_data['email']}"] = {
            "risk": probability,
            "prediction": prediction,
            "inputs": {
                "age": age, "sex": sex_value, "cp": cp, "trestbps": trestbps, "chol": chol,
                "fbs": fbs, "restecg": restecg, "thalach": thalach, "exang": exang,
                "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal
            }
        }
        st.rerun()

    # Retrieve last prediction from session
    last_pred_key = f"last_pred_heart_{patient_data['email']}"
    if last_pred_key in st.session_state:
        pred_res = st.session_state[last_pred_key]
        prob = pred_res["risk"]
        pred = pred_res["prediction"]

        # ---- 4. Risk Card & Gauge ----
        st.markdown('<div class="section-header">📊 Risk Assessment Results</div>', unsafe_allow_html=True)
        
        col_res1, col_res2, col_res3 = st.columns([1, 1, 1.2])
        with col_res1:
            if pred == 1:
                result_card("error", "Cardiovascular Concern Detected", 
                            "The predictive model indicates patient parameters show signs of potential cardiovascular disease risks.")
            else:
                result_card("success", "Cardiovascular Parameters Normal", 
                            "The predictive model indicates patient parameters fall within standard cardiac ranges.")
            
            custom_metric_card("Heart Risk Probability", f"{prob*100:.2f}%", "#EF4444" if pred == 1 else "#22C55E")
        
        with col_res2:
            st.plotly_chart(draw_risk_gauge(prob * 100, "Cardiac Risk Dial"), use_container_width=True)

        with col_res3:
            st.plotly_chart(draw_xai_feature_contributions("Heart Disease", pred_res["inputs"]), use_container_width=True)

        # ---- 5. Phase 4 AI Recommendation Panel ----
        patient_data_full = db.get_user(patient_data['email']) or patient_data
        rec_obj = get_recommendation("Heart Disease", prob, patient_data_full, pred_res["inputs"])

        # Auto-trigger emergency if CRITICAL
        if rec_obj.get("emergency"):
            st.session_state["specialist_disease"]   = "Heart Disease"
            st.session_state["specialist_risk"]       = prob
            st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
            st.session_state["specialist_type"]       = rec_obj["specialist"]
            st.session_state["specialist_emergency"]  = True
            st.session_state["specialist_rec_obj"]    = rec_obj

        # Confidence display row (Phase 4 M6/EX-1)
        model_info = get_model_info("Heart Disease", prob)
        prediction_confidence_row(
            risk_pct=prob * 100,
            confidence_pct=model_info["confidence_pct"],
            model_name=model_info["model_name"]
        )

        ai_recommendation_panel(
            "Heart Disease", prob,
            rec_obj.get("explanation", ""),
            recommendations["Heart Disease"],
            rec_obj.get("department", "Cardiovascular Medicine & Surgery"),
            rec_obj=rec_obj
        )

        # ---- 5b. Find Specialist Button ----
        col_find, col_remind = st.columns(2)
        with col_find:
            if st.button("🏥 Find Nearby Cardiologists", key="find_cardio_btn", use_container_width=True):
                st.session_state["specialist_disease"]   = "Heart Disease"
                st.session_state["specialist_risk"]       = prob
                st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
                st.session_state["specialist_type"]       = "Cardiologist"
                st.session_state["specialist_emergency"]  = rec_obj.get("emergency", False)
                st.session_state["specialist_rec_obj"]    = rec_obj
                st.session_state.page = "Specialist Finder"
                st.rerun()
        with col_remind:
            if rec_obj["risk_level"] in ["HIGH", "CRITICAL"]:
                if st.button("💊 Set Health Reminder", key="heart_reminder_toggle", use_container_width=True):
                    st.session_state["show_heart_reminder"] = not st.session_state.get("show_heart_reminder", False)

        if st.session_state.get("show_heart_reminder"):
            followup_reminder_form("Heart Disease")

        # ---- 6. Download ----
        st.markdown('<div class="section-header">📄 Official Clinical Report</div>', unsafe_allow_html=True)
        
        pdf_path = generate_single_report_pdf(
            "Heart Disease", prob, pred, recommendations["Heart Disease"]
        )
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Heart Disease Report PDF",
                data=f,
                file_name=f"Heart_Disease_Report_{patient_data['name'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        if st.button("✉️ Email Report PDF to Registered Address", key="email_report_heart", use_container_width=True):
            st.success(f"Clinical report PDF successfully dispatched to: {patient_data['email']} (Simulated)")
            db.add_notification(patient_data['email'], "Copy of your Cardiovascular Risk Screening Report PDF has been emailed to you.")
