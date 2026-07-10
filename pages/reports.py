# Reports page with interactive Analytics Dashboard (Priority 10)
import streamlit as st
from components.cards import custom_metric_card, result_card, report_preview_card
from components.charts import draw_monthly_trends, draw_accuracy_overview, draw_disease_distribution
from utils.helpers import get_report_history
from utils.pdf_generator import (
    generate_pdf_report, 
    recommendations, 
    display_medical_history
)
import utils.database as db

def show(page_title="📄 Healthcare Report Center"):
    theme = st.session_state.get("theme", "Ethereal Silk (Light)")
    if theme == "Midnight Cosmic (Dark)":
        accent_css = """
        <style>
        :root {
            --accent: #94A3B8;
            --accent-light: #CBD5E1;
            --accent-dark: #475569;
            --accent-bg: rgba(148, 163, 184, 0.12);
            --nav-hover: rgba(148, 163, 184, 0.15);
        }
        </style>
        """
    else:
        accent_css = """
        <style>
        :root {
            --accent: #475569;
            --accent-light: #64748B;
            --accent-dark: #334155;
            --accent-bg: rgba(71, 85, 105, 0.08);
            --nav-hover: rgba(71, 85, 105, 0.08);
        }
        </style>
        """
    st.markdown(accent_css, unsafe_allow_html=True)
    st.header(page_title)

    role = st.session_state.get("user_role", "Patient")
    email = st.session_state.get("user_email", "")

    # Pull history logs from SQLite
    history = db.get_predictions(None if role == "Doctor" else email)
    reports = st.session_state.get("reports", {})

    # Create tabs: One for Full Report Generator, one for Analytics, one for Historical Log
    tab1, tab2, tab3 = st.tabs(["📋 Current Risk Assessment", "📊 Analytics Dashboard", "📜 Historical Reports Log"])

    with tab1:
        if len(reports) == 0:
            st.warning("No screening data is active for this session. Please perform at least one disease prediction.")
        else:
            st.subheader("Session Health Summary")
            
            report_type = st.selectbox(
                "Select Report Type",
                ["Full Health Report", *reports.keys()],
                key="report_type_selector"
            )

            specialists = {
                "Diabetes": "Endocrinologist",
                "Heart Disease": "Cardiologist",
                "Kidney Disease": "Nephrologist",
                "Readmission": "Internal Medicine Specialist"
            }

            if report_type == "Full Health Report":
                st.write("---")
                cols = st.columns(len(reports))
                total_risk = 0
                specialist_set = set()

                for idx, (disease, data) in enumerate(reports.items()):
                    risk = data["risk"] * 100
                    total_risk += risk
                    specialist_set.add(specialists.get(disease, "General Practitioner"))
                    
                    with cols[idx]:
                        custom_metric_card(disease, f"{risk:.2f}%")

                overall_risk = total_risk / len(reports)
                
                st.markdown('<div class="section-header">Overall Risk Status</div>', unsafe_allow_html=True)
                
                if overall_risk >= 70:
                    result_card("error", f"HIGH RISK — {overall_risk:.2f}%", "Immediate specialist consultation is highly recommended.")
                elif overall_risk >= 40:
                    result_card("warning", f"MODERATE RISK — {overall_risk:.2f}%", "Lifestyle modifications and clinical follow-ups are advised.")
                else:
                    result_card("success", f"LOW RISK — {overall_risk:.2f}%", "Continue preventive health measures and normal checks.")

                st.subheader("Recommended Specialists")
                for doctor in specialist_set:
                    st.write(f"✓ {doctor}")

                st.subheader("🏃 Personalized Health Recommendations")
                for disease in reports.keys():
                    st.markdown(f"**{disease}**")
                    for item in recommendations.get(disease, []):
                        st.write(f"✓ {item}")
                    st.write("")

                st.subheader("📋 Detailed Medical History fields")
                for disease in reports.keys():
                    st.markdown(f"**{disease} Details**")
                    display_medical_history(disease)
                    st.divider()

                pdf_file = generate_pdf_report(
                    reports,
                    overall_risk,
                    specialist_set,
                    recommendations
                )

                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="📄 Download Comprehensive PDF Report",
                        data=file,
                        file_name="Healthcare_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            else:
                st.write("---")
                data = reports[report_type]
                risk = data["risk"] * 100
                prediction = data["prediction"]

                st.subheader(f"Detailed Report: {report_type}")
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    custom_metric_card("Risk Probability", f"{risk:.2f}%", "#EF4444" if prediction == 1 else "#22C55E")
                with col_r2:
                    custom_metric_card("Assessment Status", "At Risk" if prediction == 1 else "Low Risk", "#EF4444" if prediction == 1 else "#22C55E")

                result_card("info", f"Recommended Specialist: {specialists.get(report_type, 'Specialist')}", 
                            f"We advise scheduling an appointment with a/an {specialists.get(report_type, 'Specialist')} for specialized examination.")

                st.subheader("Lifestyle Recommendations")
                for item in recommendations.get(report_type, []):
                    st.write(f"✓ {item}")

    with tab2:
        # -------------------------
        # ANALYTICS DASHBOARD (Priority 10)
        # -------------------------
        st.subheader("📊 Clinical Diagnostic Analytics")
        if len(history) == 0:
            st.info("No logs available to compile stats. Perform a prediction first.")
        else:
            # Metrics
            pred_count = len(history)
            avg_risk = sum(h["risk"] for h in history) / pred_count * 100
            
            # Most common disease
            disease_counts = {}
            for h in history:
                disease_counts[h["disease"]] = disease_counts.get(h["disease"], 0) + 1
            most_common = max(disease_counts, key=disease_counts.get) if disease_counts else "N/A"

            # Render HTML metrics
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                custom_metric_card("Total Diagnostic Logs", str(pred_count), "#0F6E84")
            with mc2:
                custom_metric_card("Average Risk Rating", f"{avg_risk:.1f}%", "#1AA7C8")
            with mc3:
                custom_metric_card("Prevalent Screening", most_common, "#0F3D4F")

            st.divider()

            # Plotly Charts
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("<div style='text-align:center;font-weight:600;color:#0F3D4F;'>Monthly Diagnostics Risk Trend</div>", unsafe_allow_html=True)
                st.plotly_chart(draw_monthly_trends(history), use_container_width=True)
            with col_chart2:
                st.markdown("<div style='text-align:center;font-weight:600;color:#0F3D4F;'>Classifier Accuracy Matrix</div>", unsafe_allow_html=True)
                st.plotly_chart(draw_accuracy_overview(), use_container_width=True)

    with tab3:
        st.subheader("Prediction History Log")
        if len(history) == 0:
            st.info("No prediction records found in the database.")
        else:
            for entry in history:
                label = f"{entry['disease']} (Patient: {entry['patient_email']})" if role == "Doctor" else entry["disease"]
                report_preview_card(
                    label,
                    entry["risk"],
                    entry["timestamp"],
                    entry["prediction"]
                )
                
                # Expandable parameters view
                with st.expander("Show clinical parameters for this prediction"):
                    import json
                    try:
                        inputs = json.loads(entry["inputs_json"])
                        st.json(inputs)
                    except Exception:
                        st.write("Parameters details could not be parsed.")
