# Kidney disease prediction page with clinical flow, Plotly gauges, and Phase 4 AI Recommendation System
import streamlit as st
from components.cards import custom_metric_card, result_card, patient_profile_card, ai_recommendation_panel, followup_reminder_form, prediction_confidence_row
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
            --accent: #60A5FA;
            --accent-light: #93C5FD;
            --accent-dark: #2563EB;
            --accent-bg: rgba(96, 165, 250, 0.12);
            --nav-hover: rgba(96, 165, 250, 0.15);
        }
        </style>
        """
    else:
        accent_css = """
        <style>
        :root {
            --accent: #2563EB;
            --accent-light: #60A5FA;
            --accent-dark: #1D4ED8;
            --accent-bg: rgba(37, 99, 235, 0.08);
            --nav-hover: rgba(37, 99, 235, 0.08);
        }
        </style>
        """
    st.markdown(accent_css, unsafe_allow_html=True)
    st.header("🧬 Chronic Kidney Disease Risk Screening")

    # ---- 1. Patient Selection / Info ----
    st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
    
    role = st.session_state.get("user_role", "Patient")
    
    if role == "Doctor":
        conn = db.get_connection()
        rows = conn.execute("SELECT * FROM users WHERE role = 'Patient'").fetchall()
        conn.close()
        patients = [dict(r) for r in rows]
        
        patient_options = {p["email"]: f"{p['name']} ({p['email']})" for p in patients}
        selected_patient_email = st.selectbox("Select Patient to Screen", list(patient_options.keys()), format_func=lambda x: patient_options[x], key="kidney_patient_select")
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
        age = st.number_input("Age", 1, 120, 45, key="kidney_age")
        bp = st.number_input("Blood Pressure (mm Hg)", 50, 250, 80, key="kidney_bp")
        sg = st.selectbox("Specific Gravity", [1.005, 1.010, 1.015, 1.020, 1.025], key="kidney_sg")
        al = st.selectbox("Albumin", [0, 1, 2, 3, 4, 5], key="kidney_al")
        su = st.selectbox("Sugar", [0, 1, 2, 3, 4, 5], key="kidney_su")
        rbc = st.selectbox("Red Blood Cells (0: Abnormal, 1: Normal)", [0, 1], key="kidney_rbc")
        pc = st.selectbox("Pus Cell (0: Abnormal, 1: Normal)", [0, 1], key="kidney_pc")
        pcc = st.selectbox("Pus Cell Clumps (0: Not Present, 1: Present)", [0, 1], key="kidney_pcc")
        ba = st.selectbox("Bacteria (0: Not Present, 1: Present)", [0, 1], key="kidney_ba")
        bgr = st.number_input("Blood Glucose Random (mg/dl)", 50, 600, 120, key="kidney_bgr")
        bu = st.number_input("Blood Urea (mg/dl)", 1, 400, 40, key="kidney_bu")
        sc = st.number_input("Serum Creatinine (mg/dl)", 0.0, 20.0, 1.2, key="kidney_sc")

    with col2:
        sod = st.number_input("Sodium (mEq/L)", 50, 200, 140, key="kidney_sod")
        pot = st.number_input("Potassium (mEq/L)", 1.0, 15.0, 4.5, key="kidney_pot")
        hemo = st.number_input("Hemoglobin (gms)", 1.0, 25.0, 15.0, key="kidney_hemo")
        pcv = st.number_input("Packed Cell Volume", 10, 70, 45, key="kidney_pcv")
        wc = st.number_input("White Blood Cell Count (cells/cumm)", 1000, 30000, 8000, key="kidney_wc")
        rc = st.number_input("Red Blood Cell Count (millions/cmm)", 1.0, 10.0, 5.0, key="kidney_rc")
        htn = st.selectbox("Hypertension (0: No, 1: Yes)", [0, 1], key="kidney_htn")
        dm = st.selectbox("Diabetes Mellitus (0: No, 1: Yes)", [0, 1], key="kidney_dm")
        cad = st.selectbox("Coronary Artery Disease (0: No, 1: Yes)", [0, 1], key="kidney_cad")
        appet = st.selectbox("Appetite (0: Good, 1: Poor)", [0, 1], key="kidney_appet")
        pe = st.selectbox("Pedal Edema (0: No, 1: Yes)", [0, 1], key="kidney_pe")
        ane = st.selectbox("Anemia (0: No, 1: Yes)", [0, 1], key="kidney_ane")

    # ---- 3. Predict Button ----
    st.markdown("---")
    if st.button("🔮 Calculate Kidney Disease Risk", key="predict_kidney", use_container_width=True):
        models = get_models()
        features = [[
            age, bp, sg, al, su,
            rbc, pc, pcc, ba,
            bgr, bu, sc, sod, pot,
            hemo, pcv, wc, rc,
            htn, dm, cad,
            appet, pe, ane
        ]]

        prediction = models["kidney"].predict(features)[0]
        probability = models["kidney"].predict_proba(features)[0][1]

        # Save to database
        save_to_history("Kidney Disease", prediction, probability, {
            "age": age, "bp": bp, "sg": sg, "al": al, "su": su,
            "rbc": rbc, "pc": pc, "pcc": pcc, "ba": ba,
            "bgr": bgr, "bu": bu, "sc": sc, "sod": sod, "pot": pot,
            "hemo": hemo, "pcv": pcv, "wc": wc, "rc": rc,
            "htn": htn, "dm": dm, "cad": cad,
            "appet": appet, "pe": pe, "ane": ane
        })

        # Save prediction results locally in session
        st.session_state[f"last_pred_kidney_{patient_data['email']}"] = {
            "risk": probability,
            "prediction": prediction,
            "inputs": {
                "age": age, "bp": bp, "sg": sg, "al": al, "su": su,
                "rbc": rbc, "pc": pc, "pcc": pcc, "ba": ba,
                "bgr": bgr, "bu": bu, "sc": sc, "sod": sod, "pot": pot,
                "hemo": hemo, "pcv": pcv, "wc": wc, "rc": rc,
                "htn": htn, "dm": dm, "cad": cad,
                "appet": appet, "pe": pe, "ane": ane
            }
        }
        st.rerun()

    # Retrieve last prediction from session
    last_pred_key = f"last_pred_kidney_{patient_data['email']}"
    if last_pred_key in st.session_state:
        pred_res = st.session_state[last_pred_key]
        prob = pred_res["risk"]
        pred = pred_res["prediction"]

        # ---- 4. Risk Card & Gauge ----
        st.markdown('<div class="section-header">📊 Risk Assessment Results</div>', unsafe_allow_html=True)
        
        col_res1, col_res2, col_res3 = st.columns([1, 1, 1.2])
        with col_res1:
            if pred == 1:
                result_card("error", "Kidney Condition Detected", 
                            "The predictive model indicates high risk of Chronic Kidney Disease based on the clinical parameters.")
            else:
                result_card("success", "Kidney Parameters Normal", 
                            "The predictive model indicates standard, healthy renal functions.")
            
            custom_metric_card("CKD Risk Probability", f"{prob*100:.2f}%", "#EF4444" if pred == 1 else "#22C55E")
        
        with col_res2:
            st.plotly_chart(draw_risk_gauge(prob * 100, "CKD Risk Dial"), use_container_width=True)

        with col_res3:
            st.plotly_chart(draw_xai_feature_contributions("Kidney Disease", pred_res["inputs"]), use_container_width=True)

        # ---- 5. Phase 4 AI Recommendation Panel ----
        patient_data_full = db.get_user(patient_data['email']) or patient_data
        rec_obj = get_recommendation("Kidney Disease", prob, patient_data_full, pred_res["inputs"])

        if rec_obj.get("emergency"):
            st.session_state["specialist_disease"]   = "Kidney Disease"
            st.session_state["specialist_risk"]       = prob
            st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
            st.session_state["specialist_type"]       = rec_obj["specialist"]
            st.session_state["specialist_emergency"]  = True
            st.session_state["specialist_rec_obj"]    = rec_obj

        # Confidence display row (Phase 4 M6/EX-1)
        model_info = get_model_info("Kidney Disease", prob)
        prediction_confidence_row(
            risk_pct=prob * 100,
            confidence_pct=model_info["confidence_pct"],
            model_name=model_info["model_name"]
        )

        ai_recommendation_panel(
            "Kidney Disease", prob,
            rec_obj.get("explanation", ""),
            recommendations["Kidney Disease"],
            rec_obj.get("department", "Nephrology & Renal Medicine"),
            rec_obj=rec_obj
        )

        col_find, col_remind = st.columns(2)
        with col_find:
            if st.button("🏥 Find Nearby Nephrologists", key="find_nephro_btn", use_container_width=True):
                st.session_state["specialist_disease"]   = "Kidney Disease"
                st.session_state["specialist_risk"]       = prob
                st.session_state["specialist_risk_level"] = rec_obj["risk_level"]
                st.session_state["specialist_type"]       = "Nephrologist"
                st.session_state["specialist_emergency"]  = rec_obj.get("emergency", False)
                st.session_state["specialist_rec_obj"]    = rec_obj
                st.session_state.page = "Specialist Finder"
                st.rerun()
        with col_remind:
            if rec_obj["risk_level"] in ["HIGH", "CRITICAL"]:
                if st.button("💊 Set Health Reminder", key="kidney_reminder_toggle", use_container_width=True):
                    st.session_state["show_kidney_reminder"] = not st.session_state.get("show_kidney_reminder", False)
        if st.session_state.get("show_kidney_reminder"):
            followup_reminder_form("Kidney Disease")

        # ---- 6. Download ----
        st.markdown('<div class="section-header">📄 Official Clinical Report</div>', unsafe_allow_html=True)
        
        pdf_path = generate_single_report_pdf(
            "Kidney Disease", prob, pred, recommendations["Kidney Disease"]
        )
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Kidney Disease Report PDF",
                data=f,
                file_name=f"Kidney_Report_{patient_data['name'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        if st.button("✉️ Email Report PDF to Registered Address", key="email_report_kidney", use_container_width=True):
            st.success(f"Clinical report PDF successfully dispatched to: {patient_data['email']} (Simulated)")
            db.add_notification(patient_data['email'], "Copy of your Chronic Kidney Disease Risk Screening Report PDF has been emailed to you.")
