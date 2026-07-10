# Diabetes prediction page with clinical flow, Plotly gauges, and Phase 4 AI Recommendation System
import streamlit as st
from components.cards import custom_metric_card, result_card, patient_profile_card, ai_recommendation_panel, prediction_confidence_row, followup_reminder_form
from components.charts import draw_risk_gauge, draw_xai_feature_contributions
from utils.helpers import get_models, save_to_history, get_model_info
import utils.database as db
from utils.pdf_generator import recommendations, generate_single_report_pdf
from utils.recommendation_engine import get_recommendation

def show():
    theme = st.session_state.get("theme", "Ethereal Silk (Light)")
    if theme == "Midnight Cosmic (Dark)":
        accent_css = """
        <style>
        :root {
            --accent: #FBBF24;
            --accent-light: #FDE047;
            --accent-dark: #D97706;
            --accent-bg: rgba(251, 191, 36, 0.12);
            --nav-hover: rgba(251, 191, 36, 0.15);
        }
        </style>
        """
    else:
        accent_css = """
        <style>
        :root {
            --accent: #D97706;
            --accent-light: #F59E0B;
            --accent-dark: #92400E;
            --accent-bg: rgba(217, 119, 6, 0.08);
            --nav-hover: rgba(217, 119, 6, 0.08);
        }
        </style>
        """
    st.markdown(accent_css, unsafe_allow_html=True)
    st.header("🩺 Diabetes Risk Screening")

    # ---- 1. Patient Selection / Info (Priority 2) ----
    st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
    
    role = st.session_state.get("user_role", "Patient")
    
    if role == "Doctor":
        # Get list of patients from db
        conn = db.get_connection()
        rows = conn.execute("SELECT * FROM users WHERE role = 'Patient'").fetchall()
        conn.close()
        patients = [dict(r) for r in rows]
        
        patient_options = {p["email"]: f"{p['name']} ({p['email']})" for p in patients}
        selected_patient_email = st.selectbox("Select Patient to Screen", list(patient_options.keys()), format_func=lambda x: patient_options[x])
        patient_data = db.get_user(selected_patient_email)
    else:
        patient_data = db.get_user(st.session_state.get("user_email"))

    if patient_data:
        patient_profile_card(patient_data)
    else:
        st.warning("Patient profile details could not be loaded.")

    # ---- 2. Clinical Inputs ----
    st.markdown('<div class="section-header">🔬 Clinical Information Inputs</div>', unsafe_allow_html=True)

    gender = st.selectbox("Gender", ["Female", "Male"], key="diabetes_gender")

    if "pregnancies" not in st.session_state:
        st.session_state.pregnancies = 1
    if "glucose" not in st.session_state:
        st.session_state.glucose = 120
    if "bp" not in st.session_state:
        st.session_state.bp = 70
    if "skin" not in st.session_state:
        st.session_state.skin = 20
    if "insulin" not in st.session_state:
        st.session_state.insulin = 80
    if "bmi" not in st.session_state:
        st.session_state.bmi = 25.0
    if "dpf" not in st.session_state:
        st.session_state.dpf = 0.5
    if "age" not in st.session_state:
        st.session_state.age = 30

    if st.button("📋 Load Sample Diabetic Patient Profile", key="diabetes_sample"):
        st.session_state.pregnancies = 6
        st.session_state.glucose = 165
        st.session_state.bp = 88
        st.session_state.skin = 35
        st.session_state.insulin = 210
        st.session_state.bmi = 36.5
        st.session_state.dpf = 0.85
        st.session_state.age = 52
        st.rerun()

    if gender == "Male":
        pregnancies = 0
        st.info("Pregnancies automatically set to 0 for male patients.")
    else:
        pregnancies = st.number_input("Pregnancies Count", min_value=0, max_value=20, key="pregnancies")

    col1, col2 = st.columns(2)
    with col1:
        glucose = st.number_input("Plasma Glucose Concentration (2 hours in oral glucose tolerance test)", min_value=0, max_value=300, key="glucose")
        skin = st.number_input("Triceps Skin Fold Thickness (mm)", min_value=0, max_value=100, key="skin")
        bmi = st.number_input("Body Mass Index (Weight in kg/(Height in m)^2)", min_value=0.0, max_value=70.0, key="bmi")
        age = st.number_input("Age (years)", min_value=1, max_value=100, key="age")
    with col2:
        bp = st.number_input("Diastolic Blood Pressure (mm Hg)", min_value=0, max_value=200, key="bp")
        insulin = st.number_input("2-Hour Serum Insulin (mu U/ml)", min_value=0, max_value=900, key="insulin")
        dpf = st.number_input("Diabetes Pedigree Function (DPF)", min_value=0.0, max_value=5.0, key="dpf")

    # ---- 3. Predict Button ----
    st.markdown("---")
    if st.button("🔮 Calculate Diabetes Risk", key="predict_diabetes", use_container_width=True):
        models = get_models()
        features = [[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]]

        prediction = models["diabetes"].predict(features)[0]
        probability = models["diabetes"].predict_proba(features)[0][1]

        # Save to database (patient_data["email"])
        save_to_history("Diabetes", prediction, probability, {
            "pregnancies": pregnancies, "glucose": glucose, "bp": bp, "skin": skin,
            "insulin": insulin, "bmi": bmi, "dpf": dpf, "age": age
        })

        # Set prediction details for active patient
        st.session_state[f"last_pred_diabetes_{patient_data['email']}"] = {
            "risk": probability,
            "prediction": prediction,
            "inputs": {
                "pregnancies": pregnancies, "glucose": glucose, "bp": bp, "skin": skin,
                "insulin": insulin, "bmi": bmi, "dpf": dpf, "age": age
            }
        }
        st.rerun()

    # Retrieve last prediction from session for this patient to display results persistently
    last_pred_key = f"last_pred_diabetes_{patient_data['email']}"
    if last_pred_key in st.session_state:
        pred_res = st.session_state[last_pred_key]
        prob = pred_res["risk"]
        pred = pred_res["prediction"]

        # ---- 4. Risk Card & Gauge (Priority 2) ----
        st.markdown('<div class="section-header">📊 Risk Assessment Results</div>', unsafe_allow_html=True)
        
        col_res1, col_res2, col_res3 = st.columns([1, 1, 1.2])
        with col_res1:
            if pred == 1:
                result_card("error", "Diabetic Risk Detected", 
                            "The predictive model indicates patient parameters are highly correlated with diabetes mellitus.")
            else:
                result_card("success", "Low Diabetes Risk Detected", 
                            "The predictive model indicates patient parameters align with healthy clinical ranges.")
            
            custom_metric_card("Diabetes Probability", f"{prob*100:.2f}%", "#EF4444" if pred == 1 else "#22C55E")
        
        with col_res2:
            st.plotly_chart(draw_risk_gauge(prob * 100, "Diabetes Risk Dial"), use_container_width=True)

        with col_res3:
            st.plotly_chart(draw_xai_feature_contributions("Diabetes", pred_res["inputs"]), use_container_width=True)

        # ---- 5. Phase 4 AI Recommendation Panel ----
        patient_data_full = db.get_user(patient_data['email']) or patient_data
        rec_obj = get_recommendation("Diabetes", prob, patient_data_full, pred_res["inputs"])

        # Auto-trigger emergency if CRITICAL
        if rec_obj.get("emergency"):
            st.session_state["specialist_disease"]   = "Diabetes"
            st.session_state["specialist_risk"]       = prob
            st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
            st.session_state["specialist_type"]       = rec_obj["specialist"]
            st.session_state["specialist_emergency"]  = True
            st.session_state["specialist_rec_obj"]    = rec_obj

        # Confidence display row (Phase 4 M6/EX-1)
        model_info = get_model_info("Diabetes", prob)
        prediction_confidence_row(
            risk_pct=prob * 100,
            confidence_pct=model_info["confidence_pct"],
            model_name=model_info["model_name"]
        )

        ai_recommendation_panel(
            "Diabetes", prob,
            rec_obj.get("explanation", ""),
            recommendations["Diabetes"],
            rec_obj.get("department", "Endocrinology & Metabolics"),
            rec_obj=rec_obj
        )

        # ---- 5b. Find Specialist Button ----
        col_find, col_remind = st.columns(2)
        with col_find:
            if st.button("🏥 Find Nearby Endocrinologists", key="find_endo_btn", use_container_width=True):
                st.session_state["specialist_disease"]   = "Diabetes"
                st.session_state["specialist_risk"]       = prob
                st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
                st.session_state["specialist_type"]       = "Endocrinologist"
                st.session_state["specialist_emergency"]  = rec_obj.get("emergency", False)
                st.session_state["specialist_rec_obj"]    = rec_obj
                st.session_state.page = "Specialist Finder"
                st.rerun()
        with col_remind:
            if rec_obj["risk_level"] in ["HIGH", "CRITICAL"]:
                if st.button("💊 Set Health Reminder", key="diabetes_reminder_toggle", use_container_width=True):
                    st.session_state["show_diabetes_reminder"] = not st.session_state.get("show_diabetes_reminder", False)

        if st.session_state.get("show_diabetes_reminder"):
            followup_reminder_form("Diabetes")

        # ---- 6. Download (Priority 2) ----
        st.markdown('<div class="section-header">📄 Official Clinical Report</div>', unsafe_allow_html=True)
        
        pdf_path = generate_single_report_pdf(
            "Diabetes", prob, pred, recommendations["Diabetes"]
        )
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Diabetes Screening Report PDF",
                data=f,
                file_name=f"Diabetes_Report_{patient_data['name'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        if st.button("✉️ Email Report PDF to Registered Address", key="email_report_diabetes", use_container_width=True):
            st.success(f"Clinical report PDF successfully dispatched to: {patient_data['email']} (Simulated)")
            db.add_notification(patient_data['email'], "Copy of your Diabetes Risk Screening Report PDF has been emailed to you.")
