# AI Health Assistant Chat page (Priority 7)
import streamlit as st
import utils.database as db
from datetime import datetime

def get_assistant_response(query, user_data=None, predictions=None):
    """Retrieve highly personalized context-aware clinical responses based on active patient EHR."""
    q = query.lower()
    
    # Compile a patient summary if user_data exists
    name = user_data.get("name", "Patient") if user_data else "Patient"
    meds = user_data.get("medications", "None") if user_data else "None"
    allergies = user_data.get("allergies", "None Reported") if user_data else "None Reported"
    
    # Get latest risk for each disease
    latest_risks = {}
    if predictions:
        for p in predictions:
            if p["disease"] not in latest_risks:
                latest_risks[p["disease"]] = p["risk"] * 100

    # Greeting helper
    greeting = f"Hello {name}, "
    
    if "diabet" in q or "sugar" in q or "glucose" in q:
        risk_msg = ""
        if "Diabetes" in latest_risks:
            risk_val = latest_risks["Diabetes"]
            risk_msg = f"I see your latest Diabetes risk is assessed at **{risk_val:.1f}%**. "
        
        med_warning = ""
        if meds != "None" and "metformin" not in meds.lower():
            med_warning = f"Your current active medications are listed as: *{meds}*. Always check with your doctor before adding new blood sugar stabilizers. "

        return (
            f"{greeting}{risk_msg}Based on clinical guidelines and your profile:\n\n"
            "1. **Dietary Control:** Maintain a low-glycemic index diet. Avoid refined carbohydrates and sweets.\n"
            "2. **Physical Activity:** Aim for at least 150 minutes of moderate cardio weekly.\n"
            "3. **Regular Monitoring:** Track your HbA1c and fasting blood sugar regularly.\n\n"
            f"{med_warning}Since your allergies are *{allergies}*, make sure your pharmacist is aware of any new prescriptions."
        )
        
    elif "heart" in q or "blood pressure" in q or "hypertension" in q or "cardio" in q or "cholesterol" in q:
        risk_msg = ""
        if "Heart Disease" in latest_risks:
            risk_val = latest_risks["Heart Disease"]
            risk_msg = f"I note your Cardiology risk score is **{risk_val:.1f}%**. "

        med_warning = ""
        if meds != "None":
            med_warning = f"Ensure medications listed in your EHR (*{meds}*) are taken precisely as scheduled. "

        return (
            f"{greeting}{risk_msg}To support your cardiovascular health:\n\n"
            "1. **Sodium Restriction:** Restrict sodium intake to under 2,000 mg daily.\n"
            "2. **DASH Diet:** Focus on whole grains, poultry, fish, and rich dietary fiber.\n"
            "3. **Vitals Check:** Monitor resting heart rate and blood pressure daily.\n\n"
            f"{med_warning}*Note: If you feel chest tightness, pain, or shortness of breath, please call emergency services immediately.*"
        )
        
    elif "kidney" in q or "renal" in q or "creatinine" in q:
        risk_msg = ""
        if "Kidney Disease" in latest_risks:
            risk_val = latest_risks["Kidney Disease"]
            risk_msg = f"Your renal progression risk is evaluated at **{risk_val:.1f}%**. "

        return (
            f"{greeting}{risk_msg}To protect your kidney filtration capabilities:\n\n"
            "1. **Avoid NSAIDs:** Avoid over-the-counter painkillers like ibuprofen/naproxen which directly stress kidney filters.\n"
            "2. **Hypertension Control:** Keep blood pressure strictly below 130/80 mmHg.\n"
            "3. **Fluid and Protein:** Drink adequate water daily and avoid high-protein load diets if renal function is reduced.\n\n"
            f"Please ensure annual eGFR and serum creatinine lab checks are completed."
        )
        
    elif "readmission" in q or "discharge" in q or "hospital" in q:
        risk_msg = ""
        if "Readmission" in latest_risks:
            risk_val = latest_risks["Readmission"]
            risk_msg = f"Your hospital readmission probability is calculated at **{risk_val:.1f}%**. "

        return (
            f"{greeting}{risk_msg}To ensure a safe care transition and prevent readmission:\n\n"
            "1. **Follow-up consults:** Attend follow-up physician consults within 7 to 14 days post-discharge.\n"
            "2. **Medication Adherence:** Zero missed doses of critical prescriptions.\n"
            "3. **Warning signs:** Monitor for red-flag symptoms (e.g. fever, sudden swelling, severe pain) and contact your doctor immediately."
        )
        
    elif "profile" in q or "medication" in q or "allerg" in q:
        return (
            f"{greeting}here are your current clinical data records saved in our platform:\n\n"
            f"• **Active Prescriptions:** {meds}\n"
            f"• **Allergies:** {allergies}\n"
            f"• **Blood Group:** {user_data.get('blood_group', 'Not specified')}\n"
            f"• **Risk Summary:** {', '.join([f'{d}: {v:.1f}%' for d, v in latest_risks.items()]) or 'No assessments recorded yet.'}"
        )
        
    else:
        # Default smart welcoming message
        return (
            f"{greeting}I am your AI Clinical Assistant. I have loaded your Electronic Health Record (EHR) profile.\n\n"
            "You can ask me questions such as:\n"
            "- *'How can I lower my diabetes risk?'*\n"
            "- *'What are the guidelines for kidney disease?'*\n"
            "- *'Review my clinical profile and medications.'*\n\n"
            f"Active patient record loaded: **{name}** | Prescriptions: *{meds}* | Allergies: *{allergies}*."
        )

def show():
    st.header("🤖 AI Clinical Assistant")
    st.write("Ask our context-aware clinical assistant about reducing risks, preventative guidelines, or your medical dossier details.")

    email = st.session_state.get("user_email")
    user_data = db.get_user(email)
    predictions = db.get_predictions(email)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        # Get customized greeting
        default_greeting = get_assistant_response("hello", user_data, predictions)
        st.session_state.chat_history = [
            {"role": "ai", "content": default_greeting}
        ]

    # Display chat logs
    for msg in st.session_state.chat_history:
        bubble_class = "chat-user" if msg["role"] == "user" else "chat-ai"
        align = "right" if msg["role"] == "user" else "left"
        st.markdown(f"""
        <div style="display:flex; justify-content:{'flex-end' if align == 'right' else 'flex-start'}; width:100%;">
            <div class="chat-bubble {bubble_class}">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat input form
    with st.form("chat_input_form", clear_on_submit=True):
        user_query = st.text_input("Type your medical query here...", placeholder="Can I reduce diabetes risk?")
        submit = st.form_submit_button("Send Query", use_container_width=True)

        if submit and user_query.strip():
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Generate response
            response = get_assistant_response(user_query, user_data, predictions)
            st.session_state.chat_history.append({"role": "ai", "content": response})
            st.rerun()
