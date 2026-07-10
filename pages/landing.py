# Startup Product Landing Page (Priority 10)
import streamlit as st
import pandas as pd
import os

def show():
    login_url = os.getenv("LOGIN_URL", "http://localhost:5000")
    if login_url and not login_url.startswith(("http://", "https://")):
        login_url = "https://" + login_url
    # Hero Section (Split Layout)
    col_text, col_img = st.columns([1.1, 0.9])
    
    with col_text:
        html_content = """
        <div style="padding-top: 20px; padding-right: 20px; margin-bottom: 30px;">
            <span style="background:var(--nav-hover); color:var(--primary); padding:6px 14px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; border:1px solid var(--border);">
                ✨ CLINICAL INTELLIGENCE PLATFORM
            </span>
            <h1 style="font-family: 'Lora', serif; font-size: 46px; font-weight: 700; color: var(--text); line-height: 1.2; margin: 20px 0 16px;">
                Redefining Predictive Clinical Care
            </h1>
            <p style="font-size: 16px; color: var(--text-body); line-height: 1.7; margin-bottom: 32px; font-weight: 400;">
                Lifecare integrates secure Electronic Health Records (EHR) with state-of-the-art Machine Learning diagnostics to deliver real-time, explainable risk assessments. Built for modern clinical teams and patient tracking.
            </p>
            <a href="PORTAL_URL" target="_self" style="
                background: var(--primary);
                color: white;
                padding: 14px 32px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                text-decoration: none;
                box-shadow: 0 4px 12px var(--shadow-strong);
                display: inline-block;
                transition: all 0.3s ease;
            ">Access Clinical Portal</a>
        </div>
        """.replace("PORTAL_URL", login_url)
        st.markdown(html_content, unsafe_allow_html=True)
        
    with col_img:
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/clinical_hero.png")
        try:
            st.image(img_path, **{"use_container_width": True})
        except Exception:
            try:
                st.image(img_path, **{"use_column_width": True})
            except Exception:
                st.image(img_path)
        
    st.write("")

    # ---- TRY DEMO MODE PANEL (Priority 10) ----
    st.markdown("### ⚡ Quick Demo Launch Mode")
    st.write("Bypass portal login and explore clinical roles instantly:")
    
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        if st.button("👨‍⚕️ Launch Doctor Demo (Dr. Navish)", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "Doctor"
            st.session_state.user_email = "doctor@healthcare.com"
            st.session_state.user_name = "Dr. Navish"
            st.session_state.page = "Dashboard"
            st.success("Doctor demo profile loaded.")
            st.rerun()
            
    with col_d2:
        if st.button("🧑 Launch Patient Demo (John Doe)", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "Patient"
            st.session_state.user_email = "patient@healthcare.com"
            st.session_state.user_name = "John Doe"
            st.session_state.page = "Dashboard"
            st.success("Patient demo profile loaded.")
            st.rerun()

    with col_d3:
        if st.button("🛡️ Launch Admin Console Demo", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "Admin"
            st.session_state.user_email = "admin@healthcare.com"
            st.session_state.user_name = "System Admin"
            st.session_state.page = "Dashboard"
            st.success("Admin demo console loaded.")
            st.rerun()

    st.write("")

    # Core Features Row
    st.markdown("### 🛠️ Integrated Clinical Modules")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="clinical-feature-card">
            <div class="feature-icon">🩺</div>
            <h4>Diabetes Screening</h4>
            <p>Evaluates risk thresholds based on demographic parameters and metabolic profiles.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="clinical-feature-card">
            <div class="feature-icon">❤️</div>
            <h4>Cardiology Risk</h4>
            <p>Identifies coronary artery disease indicators via resting and active clinical outputs.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="clinical-feature-card">
            <div class="feature-icon">🧬</div>
            <h4>Renal Function</h4>
            <p>Calculates chronic kidney disease progression indicators from biochemical inputs.</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="clinical-feature-card">
            <div class="feature-icon">🏥</div>
            <h4>Care Transitions</h4>
            <p>Classifies hospital readmission probabilities within 30 days post-discharge.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ML Classifier Accuracies Table
    st.markdown("### 📊 Clinical Classifier Accuracy Metrics")
    st.markdown("""
    Our diagnostic models are trained on curated clinical research cohorts and optimized for low false-negative ratings:
    """)
    acc_data = [
        ["Diabetes Risk model", "77.9% Accuracy", "0.823 ROC-AUC", "Pima Indians Dataset"],
        ["Cardiovascular model", "78.7% Accuracy", "0.856 ROC-AUC", "UCI Cleveland Heart Dataset"],
        ["Chronic Kidney model", "98.8% Accuracy", "1.000 ROC-AUC", "UCI Chronic Kidney Disease Cohort"],
        ["Encounter Readmission model", "66.3% Accuracy", "0.687 ROC-AUC", "100k+ Clinical Encounters"]
    ]
    df = pd.DataFrame(acc_data, columns=["Diagnostic Classifier", "Accuracy Score", "Area Under ROC", "Training Cohort Source"])
    st.table(df)

    st.divider()

    # Team & Doctors
    st.markdown("### 👨‍⚕️ Medical Advisory Board")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("""
        <div style="background:var(--card); padding:28px 24px; border-radius:20px; border:1px solid var(--border); text-align:center; box-shadow:0 4px 16px var(--shadow);">
            <img src="https://api.dicebear.com/7.x/adventurer/svg?seed=drnavish" style="width:84px;height:84px;border-radius:50%;margin-bottom:14px;border:3px solid var(--primary);"/>
            <h4 style="margin:0 0 6px; color:var(--text);">Dr. Navish</h4>
            <p style="color:var(--primary); font-size:13.5px; font-weight:700; margin-bottom:8px;">Chief Medical Officer</p>
            <p style="color:var(--text-body); font-size:13px; margin:0; line-height:1.5;">Specializes in endocrinology and medical data informatics systems.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d2:
        st.markdown("""
        <div style="background:var(--card); padding:28px 24px; border-radius:20px; border:1px solid var(--border); text-align:center; box-shadow:0 4px 16px var(--shadow);">
            <img src="https://api.dicebear.com/7.x/adventurer/svg?seed=sarah" style="width:84px;height:84px;border-radius:50%;margin-bottom:14px;border:3px solid var(--primary);"/>
            <h4 style="margin:0 0 6px; color:var(--text);">Dr. Sarah Jenkins</h4>
            <p style="color:var(--primary); font-size:13.5px; font-weight:700; margin-bottom:8px;">Lead Nephrologist</p>
            <p style="color:var(--text-body); font-size:13px; margin:0; line-height:1.5;">Specializes in Chronic Kidney Disease diagnostic workflows.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d3:
        st.markdown("""
        <div style="background:var(--card); padding:28px 24px; border-radius:20px; border:1px solid var(--border); text-align:center; box-shadow:0 4px 16px var(--shadow);">
            <img src="https://api.dicebear.com/7.x/adventurer/svg?seed=mark" style="width:84px;height:84px;border-radius:50%;margin-bottom:14px;border:3px solid var(--primary);"/>
            <h4 style="margin:0 0 6px; color:var(--text);">Dr. Marcus Vance</h4>
            <p style="color:var(--primary); font-size:13.5px; font-weight:700; margin-bottom:8px;">Chief Cardiologist</p>
            <p style="color:var(--text-body); font-size:13px; margin:0; line-height:1.5;">Specializes in preventive cardiology and risk modeling.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Patient Testimonials
    st.markdown("### 💬 Patient Testimonials")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("""
        <div class="testimonial-card">
            <p class="quote">"Lifecare made it extremely easy to calculate and track my diabetes risk. The personalized reports let me consult my doctor with precise numbers."</p>
            <p class="author">— David K., Active Patient</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown("""
        <div class="testimonial-card">
            <p class="quote">"Using the cardiology risk models on patient cohorts helps me identify high-risk patients before symptom onset. Highly recommended."</p>
            <p class="author">— Dr. Jenkins, Advising Physician</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="text-align:center; color:var(--text-soft); font-size:12px; margin-top:50px; border-top:1px solid var(--border); padding-top:20px;">
        © 2026 Lifecare Clinical Systems Inc. All rights reserved. Powered by machine learning.
    </div>
    """, unsafe_allow_html=True)

