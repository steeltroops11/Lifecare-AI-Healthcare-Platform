# Interactive Profile page with SQLite integration
import streamlit as st
import utils.database as db
from components.cards import patient_profile_card

def show():
    theme = st.session_state.get("theme", "Ethereal Silk (Light)")
    if theme == "Midnight Cosmic (Dark)":
        accent_css = """
        <style>
        :root {
            --accent: #818CF8;
            --accent-light: #A5B4FC;
            --accent-dark: #4F46E5;
            --accent-bg: rgba(129, 140, 248, 0.12);
            --nav-hover: rgba(129, 140, 248, 0.15);
        }
        </style>
        """
    else:
        accent_css = """
        <style>
        :root {
            --accent: #4F46E5;
            --accent-light: #818CF8;
            --accent-dark: #3730A3;
            --accent-bg: rgba(79, 70, 229, 0.08);
            --nav-hover: rgba(79, 70, 229, 0.08);
        }
        </style>
        """
    st.markdown(accent_css, unsafe_allow_html=True)
    st.header("👤 Profile & Clinical Details Management")

    email = st.session_state.get("user_email")
    user_data = db.get_user(email)

    if not user_data:
        st.error("Profile data not found.")
        return

    # Left: Card view, Right: Edit Form
    col_view, col_edit = st.columns([1, 1])

    with col_view:
        st.subheader("Current Card Preview")
        patient_profile_card(user_data)
        st.write("")
        # Display EHR Card (Priority 2)
        from components.cards import ehr_summary_card
        ehr_summary_card(user_data)

    with col_edit:
        st.subheader("Edit Profile & EHR Fields")
        with st.form("profile_edit_form"):
            name = st.text_input("Full Name", value=user_data.get("name", ""))
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=user_data.get("age") or 30)
            blood_group = st.selectbox(
                "Blood Group",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(user_data.get("blood_group") or "O+")
            )
            emergency_contact = st.text_input("Emergency Contact Number", value=user_data.get("emergency_contact", ""))
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=user_data.get("weight_kg") or 70.0)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=user_data.get("height_cm") or 170.0)
            photo_url = st.text_input("Profile Avatar URL (Optional)", value=user_data.get("photo_url") or "")
            
            # EHR Inputs (Priority 2)
            st.markdown("#### Electronic Health Record Context")
            allergies = st.text_input("Allergies List", value=user_data.get("allergies", "None Reported"))
            medications = st.text_input("Active Prescriptions", value=user_data.get("medications", "None"))
            family_history = st.text_input("Family Medical History Summary", value=user_data.get("family_history", "None"))
            smoking = st.selectbox("Smoking History", ["Non-smoker", "Former Smoker", "Active Smoker"], index=["Non-smoker", "Former Smoker", "Active Smoker"].index(user_data.get("smoking") or "Non-smoker"))
            alcohol = st.selectbox("Alcohol Consumption", ["None", "Occasional", "Frequent"], index=["None", "Occasional", "Frequent"].index(user_data.get("alcohol") or "Occasional"))
            vaccinations = st.text_input("Vaccinations History", value=user_data.get("vaccinations", "Up-to-date"))
            prev_diseases = st.text_input("Previous Diseases / Surgeries", value=user_data.get("prev_diseases", "None"))
            immunocompromised = st.checkbox("Immunocompromised Patient Status (High infection risk)", value=bool(user_data.get("immunocompromised", 0)))

            submitted = st.form_submit_button("💾 Save Profile Updates", use_container_width=True)
            
            if submitted:
                # Update SQLite database profile & EHR columns
                db.update_user_profile_ehr(
                    email, age, blood_group, emergency_contact, weight, height,
                    allergies, medications, family_history, smoking, alcohol, prev_diseases, vaccinations,
                    int(immunocompromised)
                )

                # Sync back to session state
                st.session_state.user_name = name
                st.success("Profile & EHR records saved successfully!")
                st.rerun()

    # Appointment schedules
    st.divider()
    st.subheader("📅 Scheduled Clinical Appointments")
    
    appointments = db.get_appointments(email if st.session_state.get("user_role") == "Patient" else None)
    if len(appointments) == 0:
        st.info("No active appointments scheduled.")
    else:
        for appt in appointments:
            status_color = "green" if appt["status"] == "Scheduled" else "gray"
            st.markdown(f"""
            <div style="background:#f4fbfd;border-left:4px solid #0F6E84;padding:15px;border-radius:10px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <h5 style="margin:0;color:#0F3D4F;">{appt['reason']}</h5>
                    <p style="margin:4px 0 0;color:gray;font-size:13px;">📅 {appt['date_time']} | Doctor: {appt['doctor_name']}</p>
                </div>
                <span style="background:#eaf6fb;color:#0F6E84;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;">{appt['status']}</span>
            </div>
            """, unsafe_allow_html=True)
