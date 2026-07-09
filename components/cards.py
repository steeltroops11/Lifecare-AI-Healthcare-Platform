# UI card components
import streamlit as st


def load_css():
    st.markdown("""
    <style>
    /* ---- Welcome Banner ---- */
    .welcome-banner{
        position: relative;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
        padding: 40px 48px;
        border-radius: 24px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 16px 40px var(--shadow-strong);
        overflow: hidden;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .welcome-banner h2 {
        font-family: 'Lora', serif;
        font-weight: 700;
        font-size: 34px;
        margin: 0;
    }
    .welcome-banner::before{
        content: "";
        position: absolute;
        width: 320px;
        height: 320px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,.12), transparent 70%);
        top: -120px;
        right: -40px;
        pointer-events: none;
    }
    .welcome-banner::after{
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,.07), transparent 70%);
        bottom: -100px;
        left: -50px;
        pointer-events: none;
    }
    .welcome-banner h2{
        margin: 0;
        font-size: 34px;
        font-weight: 700;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
        font-family: 'Lora', serif;
    }
    .welcome-banner p{
        margin-top: 10px;
        opacity: .92;
        font-size: 17px;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    .welcome-role-badge{
        display: inline-block;
        background: rgba(255,255,255,.18);
        border: 1px solid rgba(255,255,255,.25);
        padding: 5px 16px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 12px;
        position: relative;
        z-index: 1;
    }

    /* ---- Stat Cards ---- */
    .stat-card{
        background: white;
        padding: 24px;
        border-radius: 18px;
        text-align: left;
        box-shadow: 0 4px 16px rgba(0,0,0,.06);
        transition: all .3s cubic-bezier(.4,0,.2,1);
        border: 1px solid #E8F0F3;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        border-radius: 4px 0 0 4px;
    }
    .stat-card:hover{
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,.1);
    }
    .stat-card-inner{
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .stat-card-icon{
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    .stat-card-content h1{
        margin: 0;
        font-size: 32px;
        font-weight: 800;
        line-height: 1;
    }
    .stat-card-content p{
        margin: 4px 0 0;
        color: #7B8E96;
        font-size: 14px;
        font-weight: 500;
    }

    /* ---- Prediction Module Cards ---- */
    .prediction-card{
        background: var(--card, white);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 4px 16px rgba(0,0,0,.06);
        transition: all .3s cubic-bezier(.4,0,.2,1);
        text-align: center;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--border, #E8F0F3);
    }
    .prediction-card:hover{
        transform: translateY(-6px);
        box-shadow: 0 16px 36px rgba(15,110,132,.12);
        border-color: #0F6E8430;
    }
    .prediction-icon{
        font-size: 56px;
        margin-bottom: 4px;
    }
    .prediction-title{
        font-size: 22px;
        font-weight: 700;
        margin-top: 10px;
        color: var(--text, #0F3D4F);
    }
    .prediction-text{
        color: var(--text-body, #5A7A86);
        margin-top: 8px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)


def welcome(name, role):
    st.markdown(f"""
    <div class="welcome-banner">
        <h2>🏥 Welcome {name}</h2>
        <p>{role} Dashboard | AI Powered Healthcare Analytics Platform</p>
        <span class="welcome-role-badge">{role}</span>
    </div>
    """, unsafe_allow_html=True)


def stat_card(title, value, icon="📊", color="#0F6E84"):
    st.markdown(f"""
    <div class="stat-card" style="border-left: 4px solid {color};">
        <div class="stat-card-inner">
            <div class="stat-card-icon" style="background:{color}12;color:{color};">
                {icon}
            </div>
            <div class="stat-card-content">
                <h1 style="color:{color};">{value}</h1>
                <p>{title}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def prediction_card(icon, title, description):
    st.markdown(f"""
    <div class="prediction-card">
        <div class="prediction-icon">{icon}</div>
        <div class="prediction-title">{title}</div>
        <div class="prediction-text">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def custom_metric_card(title, value, color="var(--primary)"):
    """Premium metric card replacing st.metric()."""
    st.markdown(f"""
    <div style="
        background:var(--card);
        border-radius:16px;
        padding:20px 24px;
        border:1px solid var(--border);
        border-left:4px solid {color};
        box-shadow:0 4px 15px var(--shadow);
        margin-bottom:12px;
    ">
        <p style="margin:0;color:var(--text-soft);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">{title}</p>
        <h2 style="margin:8px 0 0;color:var(--text);font-family:'Lora', serif;font-size:28px;font-weight:700;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def result_card(card_type, title, message):
    """Premium result card replacing st.success/warning/error."""
    colors = {
        "success": {"bg": "var(--success-bg)", "border": "var(--success)", "icon": "✅", "text": "var(--text)"},
        "warning": {"bg": "var(--warning-bg)", "border": "var(--warning)", "icon": "⚠️", "text": "var(--text)"},
        "error":   {"bg": "var(--danger-bg)", "border": "var(--danger)", "icon": "🔴", "text": "var(--text)"},
        "info":    {"bg": "var(--info-bg)", "border": "var(--info)", "icon": "ℹ️", "text": "var(--text)"},
    }
    c = colors.get(card_type, colors["info"])
    st.markdown(f"""
    <div style="
        background:{c['bg']};
        border:1px solid var(--border);
        border-left:4px solid {c['border']};
        border-radius:14px;
        padding:18px 22px;
        margin:12px 0;
        box-shadow:0 2px 8px var(--shadow);
    ">
        <p style="margin:0;font-size:18px;font-weight:700;color:{c['text']};">{c['icon']} {title}</p>
        <p style="margin:6px 0 0;font-size:15px;color:var(--text-body);">{message}</p>
    </div>
    """, unsafe_allow_html=True)


def report_preview_card(disease, risk, timestamp, prediction):
    """Card for displaying a report history entry."""
    status_color = "var(--danger)" if prediction == 1 else "var(--success)"
    status_text = "At Risk" if prediction == 1 else "Low Risk"
    st.markdown(f"""
    <div style="
        background:var(--card);
        border-radius:14px;
        padding:18px 22px;
        border:1px solid var(--border);
        border-left:4px solid {status_color};
        box-shadow:0 3px 12px var(--shadow);
        margin-bottom:10px;
        display:flex;
        justify-content:space-between;
        align-items:center;
    ">
        <div>
            <p style="margin:0;font-family:'Lora', serif;font-size:17px;font-weight:700;color:var(--text);">{disease}</p>
            <p style="margin:4px 0 0;font-size:13px;color:var(--text-soft);">{timestamp}</p>
        </div>
        <div style="text-align:right;">
            <p style="margin:0;font-size:20px;font-weight:800;color:{status_color};">{risk*100:.1f}%</p>
            <p style="margin:2px 0 0;font-size:12px;font-weight:600;color:{status_color};">{status_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def doctor_metric_card(title, value, subtitle, icon="👨‍⚕️", color="var(--primary)"):
    """HTML cards for doctor dashboard statistics."""
    st.markdown(f"""
    <div style="
        background:var(--card);
        border-radius:18px;
        padding:24px;
        border:1px solid var(--border);
        border-top:4px solid {color};
        box-shadow:0 6px 20px var(--shadow);
        display:flex;
        align-items:center;
        gap:20px;
        margin-bottom:16px;
    ">
        <div style="
            font-size:40px;
            background:var(--nav-hover);
            color:{color};
            width:64px;
            height:64px;
            border-radius:14px;
            display:flex;
            align-items:center;
            justify-content:center;
            flex-shrink:0;
        ">
            {icon}
        </div>
        <div>
            <p style="margin:0;color:var(--text-soft);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.3px;">{title}</p>
            <h2 style="margin:4px 0 0;color:var(--text);font-family:'Lora', serif;font-size:32px;font-weight:700;line-height:1;">{value}</h2>
            <p style="margin:4px 0 0;color:var(--text-soft);font-size:12px;">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def ai_recommendation_panel(disease, risk, explanation, recommendations_list, specialist, rec_obj=None):
    """Render a premium AI Recommendations panel (Phase 4 upgrade).
    Accepts optional rec_obj (RecommendationObject) for richer display.
    """
    risk_percentage = risk * 100

    if rec_obj:
        risk_level  = rec_obj.get("risk_level", "MODERATE")
        risk_color  = rec_obj.get("risk_color", "#F59E0B")
        risk_bg     = rec_obj.get("risk_bg", "#FFFBEB")
        risk_emoji  = rec_obj.get("risk_emoji", "\U0001f7e1")
        urgency     = rec_obj.get("urgency", "")
        emergency   = rec_obj.get("emergency", False)
        emg_msg     = rec_obj.get("emergency_msg", "")
        immediate   = rec_obj.get("immediate_actions", recommendations_list)
        lifestyle   = rec_obj.get("lifestyle", [])
        tests_list  = rec_obj.get("tests", [])
        followup    = rec_obj.get("followup", "")
        explanation = rec_obj.get("explanation", explanation)
        specialist  = rec_obj.get("department", specialist)
        text_color  = "#991B1B" if risk_level == "CRITICAL" else ("#92400E" if risk_level in ["HIGH","MODERATE"] else "#166534")
    else:
        risk_color  = "#EF4444" if risk_percentage >= 70 else ("#F59E0B" if risk_percentage >= 40 else "#22C55E")
        risk_bg     = "#FEF2F2" if risk_percentage >= 70 else ("#FFFBEB" if risk_percentage >= 40 else "#EAF9F1")
        risk_level  = "High Risk" if risk_percentage >= 70 else ("Moderate Risk" if risk_percentage >= 40 else "Low Risk")
        risk_emoji  = "\U0001f534" if risk_percentage >= 70 else ("\U0001f7e1" if risk_percentage >= 40 else "\U0001f7e2")
        text_color  = "#991B1B" if risk_percentage >= 70 else ("#92400E" if risk_percentage >= 40 else "#166534")
        urgency     = ""; emergency = False; emg_msg = ""; immediate = recommendations_list
        lifestyle   = []; tests_list = []; followup = ""

    # CRITICAL Emergency Banner
    if emergency and emg_msg:
        st.markdown(
            f'''<div style="background:#FEF2F2;border:2px solid #EF4444;border-radius:14px;
                padding:16px 20px;margin-bottom:16px;">
                <p style="margin:0;font-size:16px;font-weight:800;color:#991B1B;">\U0001f6a8 EMERGENCY ALERT</p>
                <p style="margin:6px 0 0;font-size:14px;color:#DC2626;">''' + emg_msg + '''</p>
                <p style="margin:8px 0;"><a href="tel:108" style="background:#EF4444;color:white;
                   padding:6px 16px;border-radius:8px;text-decoration:none;font-weight:700;">
                   \u260e\ufe0f CALL 108 NOW</a></p></div>''',
            unsafe_allow_html=True)

    # Urgency block
    urgency_html = ""
    if urgency:
        fp = f'<p style="margin:4px 0 0;color:{text_color};font-size:13px;">Follow-up: {followup}</p>' if followup else ""
        urgency_html = (
            f'<div style="background:{risk_bg};border-left:4px solid {risk_color};'
            f'border-radius:10px;padding:10px 16px;margin-bottom:18px;">'
            f'<p style="margin:0;color:{text_color};font-size:14px;font-weight:700;">'
            f'\u23f0 Urgency: {urgency}</p>{fp}</div>'
        )

    st.markdown(
        f'''<div style="background:rgba(255,255,255,0.7);border:1px solid #E8F0F3;border-radius:24px;
            padding:30px;backdrop-filter:blur(10px);box-shadow:0 8px 32px rgba(15,110,132,0.06);margin:20px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;
                        margin-bottom:20px;border-bottom:1px solid #E8F0F3;padding-bottom:15px;">
                <h3 style="margin:0;color:#0F3D4F;font-weight:700;">\U0001f916 AI Clinical Recommendation</h3>
                <div style="display:flex;gap:10px;align-items:center;">
                    <span style="font-size:22px;">''' + risk_emoji + f'''</span>
                    <span style="background:{risk_bg};color:{text_color};padding:6px 16px;
                                 border-radius:999px;font-size:14px;font-weight:700;">{risk_level}</span>
                </div>
            </div>
            <div style="margin-bottom:18px;">
                <h4 style="margin:0 0 6px;color:#0F3D4F;font-size:15px;font-weight:600;">
                    \U0001f50d AI Diagnosis Explanation</h4>
                <p style="margin:0;color:#4D6A75;font-size:14px;line-height:1.6;">{explanation}</p>
            </div>
            {urgency_html}
        </div>''',
        unsafe_allow_html=True)

    # Immediate Actions
    if immediate:
        actions_html = "".join(
            f'<li style="margin-bottom:6px;color:#065F46;font-size:14px;">{a}</li>' for a in immediate)
        st.markdown(
            f'''<h4 style="margin:0 0 8px;color:#0F3D4F;font-size:15px;font-weight:600;">
                \u26a1 Immediate Actions</h4>
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;
                        padding:16px 20px;margin-bottom:18px;">
                <ul style="margin:0;padding-left:18px;">''' + actions_html + '''</ul></div>''',
            unsafe_allow_html=True)

    # Recommended Tests
    if tests_list:
        tests_html = "".join(
            f'<span style="background:#EFF6FF;color:#1E40AF;padding:4px 12px;border-radius:999px;'
            f'font-size:13px;font-weight:600;margin:3px;display:inline-block;">{t}</span>'
            for t in tests_list)
        st.markdown(
            f'''<div style="margin-bottom:18px;">
                <h4 style="margin:0 0 8px;color:#0F3D4F;font-size:15px;font-weight:600;">
                    \U0001f52c Recommended Tests</h4>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">''' + tests_html + '''</div></div>''',
            unsafe_allow_html=True)

    # Lifestyle Plan
    if lifestyle:
        with st.expander("\U0001f3c3 View Personalised Lifestyle Plan"):
            life_html = "".join(
                f'<li style="margin-bottom:6px;color:#4D6A75;font-size:14px;">{item}</li>'
                for item in lifestyle)
            st.markdown(f'<ul style="margin:0;padding-left:18px;">{life_html}</ul>',
                        unsafe_allow_html=True)

    # Specialist Box
    st.markdown(
        f'''<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:16px;
            padding:16px 20px;display:flex;align-items:center;gap:15px;margin-top:8px;">
            <span style="font-size:28px;">\U0001f3e5</span>
            <div>
                <p style="margin:0;color:#1E40AF;font-size:13px;font-weight:600;text-transform:uppercase;">
                    Recommended Specialty Route</p>
                <h4 style="margin:2px 0 0;color:#1E3A8A;font-size:16px;font-weight:700;">
                    Schedule consultation with: {specialist}</h4>
            </div></div>''',
        unsafe_allow_html=True)


def patient_profile_card(user_data):
    """Premium Patient Profile Card (Priority 6)."""
    # Calculate BMI
    weight = user_data.get("weight_kg")
    height = user_data.get("height_cm")
    bmi_val = "N/A"
    bmi_status = ""
    if weight and height:
        height_m = height / 100.0
        bmi_score = weight / (height_m * height_m)
        bmi_val = f"{bmi_score:.1f}"
        if bmi_score < 18.5: bmi_status = "(Underweight)"
        elif bmi_score < 25: bmi_status = "(Normal)"
        elif bmi_score < 30: bmi_status = "(Overweight)"
        else: bmi_status = "(Obese)"

    photo_url = user_data.get("photo_url") or "https://api.dicebear.com/7.x/adventurer/svg?seed=" + user_data.get("email", "pat")
    
    st.markdown(f"""
    <div style="
        background:white;
        border-radius:24px;
        padding:30px;
        box-shadow:0 8px 30px rgba(0,0,0,0.05);
        border:1px solid #E8F0F3;
        margin-bottom:24px;
    ">
        <div style="display:flex;align-items:center;gap:24px;margin-bottom:24px;border-bottom:1px solid #EAF2F5;padding-bottom:20px;">
            <img src="{photo_url}" style="width:96px;height:96px;border-radius:50%;background:#F4FBFD;border:2px solid #0F6E84;" alt="Avatar" />
            <div>
                <h2 style="margin:0;color:#0F3D4F;font-size:26px;font-weight:800;">{user_data.get('name')}</h2>
                <span style="background:#EAF6FB;color:#0F6E84;padding:4px 12px;border-radius:999px;font-size:12px;font-weight:700;margin-top:6px;display:inline-block;">ID: {user_data.get('patient_id', 'N/A')}</span>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
            <div>
                <p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Age</p>
                <p style="margin:4px 0 0;color:#0F3D4F;font-size:16px;font-weight:700;">{user_data.get('age', 'N/A')} yrs</p>
            </div>
            <div>
                <p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Blood Group</p>
                <p style="margin:4px 0 0;color:#0F3D4F;font-size:16px;font-weight:700;">{user_data.get('blood_group', 'N/A')}</p>
            </div>
            <div>
                <p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Body Mass Index (BMI)</p>
                <p style="margin:4px 0 0;color:#0F3D4F;font-size:16px;font-weight:700;">{bmi_val} <span style="font-size:12px;color:gray;">{bmi_status}</span></p>
            </div>
            <div>
                <p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Emergency Contact</p>
                <p style="margin:4px 0 0;color:#D32F2F;font-size:15px;font-weight:700;">{user_data.get('emergency_contact', 'N/A')}</p>
            </div>
            <div>
                <p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Weight & Height</p>
                <p style="margin:4px 0 0;color:#0F3D4F;font-size:16px;font-weight:700;">{user_data.get('weight_kg', 'N/A')} kg / {user_data.get('height_cm', 'N/A')} cm</p>
            </div>
            <div>
                <p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Email Address</p>
                <p style="margin:4px 0 0;color:#0F3D4F;font-size:14px;font-weight:700;">{user_data.get('email')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def ehr_summary_card(user_data):
    """Render Electronic Health Record summary (Priority 2)."""
    immuno_banner = ""
    if user_data.get("immunocompromised", 0):
        immuno_banner = (
            '<div style="background:#FFF1F2;border:1px solid #FDA4AF;border-radius:12px;'
            'padding:12px 16px;margin-bottom:16px;text-align:center;">'
            '<span style="color:#E11D48;font-size:14px;font-weight:800;">'
            '⚠️ CRITICAL: IMMUNOCOMPROMISED PATIENT STATUS (High Infection Risk)'
            '</span></div>'
        )
    st.markdown(f"""<div style="background:white;border-radius:24px;padding:30px;box-shadow:0 8px 30px rgba(0,0,0,0.05);border:1px solid #E8F0F3;margin-bottom:24px;">
{immuno_banner}
<h3 style="margin:0 0 16px;color:#0F3D4F;border-bottom:1px solid #EAF2F5;padding-bottom:10px;">📋 Electronic Health Record (EHR)</h3>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
<div>
<p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Allergies</p>
<p style="margin:4px 0 0;color:#D32F2F;font-size:15px;font-weight:700;">{user_data.get('allergies', 'None Reported')}</p>
</div>
<div>
<p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Active Medications</p>
<p style="margin:4px 0 0;color:#0F3D4F;font-size:15px;font-weight:700;">{user_data.get('medications', 'None')}</p>
</div>
<div>
<p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Family History</p>
<p style="margin:4px 0 0;color:#0F3D4F;font-size:15px;font-weight:700;">{user_data.get('family_history', 'None')}</p>
</div>
<div>
<p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Vaccinations History</p>
<p style="margin:4px 0 0;color:#22C55E;font-size:15px;font-weight:700;">{user_data.get('vaccinations', 'Up-to-date')}</p>
</div>
<div>
<p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Smoking Status</p>
<p style="margin:4px 0 0;color:#0F3D4F;font-size:15px;font-weight:700;">{user_data.get('smoking', 'Non-smoker')}</p>
</div>
<div>
<p style="margin:0;color:#7B8E96;font-size:13px;font-weight:600;text-transform:uppercase;">Alcohol Consumption</p>
<p style="margin:4px 0 0;color:#0F3D4F;font-size:15px;font-weight:700;">{user_data.get('alcohol', 'Occasional')}</p>
</div>
</div>
</div>""", unsafe_allow_html=True)


def clinical_timeline(events):
    """Render a visual Clinical Timeline timeline list of events (Priority 1)."""
    if not events:
        st.info("No timeline events logged.")
        return

    timeline_html = """<div style="margin: 20px 0; padding-left: 20px; border-left: 3px solid var(--primary); position: relative;">"""
    for e in events:
        icon = e.get("icon", "🔵")
        title = e.get("title", "Clinical Event")
        timestamp = e.get("timestamp", "")
        desc = e.get("description", "")
        
        timeline_html += f"""
<div style="margin-bottom: 25px; position: relative;">
    <div style="
        position: absolute; 
        left: -28px; 
        top: 6px; 
        background: var(--bg); 
        border: 2px solid var(--primary); 
        border-radius: 50%; 
        width: 14px; 
        height: 14px; 
        display: flex; 
        align-items: center; 
        justify-content: center;
    "></div>
    <div style="
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px var(--shadow);
    ">
        <span style="font-size:12.5px;color:var(--text-soft);font-weight:600;">{timestamp}</span>
        <h4 style="margin:4px 0 6px;color:var(--text);font-family:'Lora', serif;font-size:16.5px;font-weight:700;">{icon} {title}</h4>
        <p style="margin:0;color:var(--text-body);font-size:14px;line-height:1.5;">{desc}</p>
    </div>
</div>"""
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)

# ============================================================
# PHASE 4 — NEW CARD COMPONENTS
# ============================================================

def prediction_confidence_row(risk_pct: float, confidence_pct: float, model_name: str):
    """Display 3-metric row: Risk % | Confidence % | Model Name (Phase 4 EX-1)."""
    risk_color = "#EF4444" if risk_pct >= 70 else ("#F59E0B" if risk_pct >= 40 else "#22C55E")
    conf_color = "#22C55E" if confidence_pct >= 85 else ("#F59E0B" if confidence_pct >= 70 else "#EF4444")

    import streamlit as st
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px 20px;
                    border-top:4px solid {risk_color};box-shadow:0 4px 14px rgba(0,0,0,.06);text-align:center;">
            <p style="margin:0;color:#7B8E96;font-size:12px;font-weight:600;text-transform:uppercase;">Risk Score</p>
            <h2 style="margin:6px 0 0;color:{risk_color};font-size:32px;font-weight:800;">{risk_pct:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px 20px;
                    border-top:4px solid {conf_color};box-shadow:0 4px 14px rgba(0,0,0,.06);text-align:center;">
            <p style="margin:0;color:#7B8E96;font-size:12px;font-weight:600;text-transform:uppercase;">Model Confidence</p>
            <h2 style="margin:6px 0 0;color:{conf_color};font-size:32px;font-weight:800;">{confidence_pct:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px 20px;
                    border-top:4px solid #0F6E84;box-shadow:0 4px 14px rgba(0,0,0,.06);text-align:center;">
            <p style="margin:0;color:#7B8E96;font-size:12px;font-weight:600;text-transform:uppercase;">Model Used</p>
            <h2 style="margin:6px 0 0;color:#0F3D4F;font-size:20px;font-weight:800;padding-top:6px;">{model_name}</h2>
        </div>
        """, unsafe_allow_html=True)


def hospital_card(facility: dict, disease: str = ""):
    """Render a ranked hospital/clinic card with ETAs and score breakdown (Phase 4)."""
    import streamlit as st
    from utils.osm_service import get_directions_url, get_osm_view_url
    import utils.database as db

    rank     = facility.get("rank", 1)
    name     = facility.get("name", "Unknown Facility")
    address  = facility.get("address", "Address not available")
    dist_km  = facility.get("distance_km", 0)
    score    = facility.get("total_score", 0)
    ftype    = facility.get("type", "clinic")
    phone    = facility.get("phone", "")
    website  = facility.get("website", "")
    lat      = facility.get("lat")
    lng      = facility.get("lng")

    # ETAs
    etas = facility.get("travel_etas", {})
    drv = etas.get("driving", 0)
    wlk = etas.get("walking", 0)
    cyc = etas.get("cycling", 0)
    eta_str = f"🚗 {drv} min drive &nbsp;·&nbsp; 🚲 {cyc} min cycle &nbsp;·&nbsp; 🚶 {wlk} min walk"

    # Score breakdown calculations
    bd = facility.get("score_breakdown", {})
    dist_pts = round(bd.get("distance", 0) * 0.40, 1)
    spec_pts = round(bd.get("specialty", 0) * 0.25, 1)
    type_pts = round(bd.get("type", 0) * 0.20, 1)
    phon_pts = round(bd.get("phone", 0) * 0.10, 1)
    web_pts  = round(bd.get("website", 0) * 0.05, 1)

    breakdown_pills = (
        f'<span style="background:#F3F4F6;color:#374151;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">📍 Prox: +{dist_pts}</span>'
        f'<span style="background:#ECFDF5;color:#047857;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">🔬 Spec: +{spec_pts}</span>'
        f'<span style="background:#EFF6FF;color:#1D4ED8;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">🏢 Type: +{type_pts}</span>'
        f'<span style="background:#FFF1F2;color:#BE123C;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">📞 Phone: +{phon_pts}</span>'
        f'<span style="background:#F5F3FF;color:#6D28D9;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">🌐 Web: +{web_pts}</span>'
    )

    rank_colors = {1: ("#FFD700", "#7B5800"), 2: ("#C0C0C0", "#3D3D3D"), 3: ("#CD7F32", "#5C2C00")}
    rb_bg, rb_text = rank_colors.get(rank, ("#EFF6FF", "#1E40AF"))
    type_icon = {"hospital": "🏥", "clinic": "🏨", "doctor": "👨‍⚕️"}.get(ftype.lower(), "🏥")
    type_label = ftype.capitalize()
    score_color = "#22C55E" if score >= 70 else ("#F59E0B" if score >= 40 else "#EF4444")
    maps_url = get_directions_url(name, lat, lng)
    patient_email = st.session_state.get("user_email", "")

    with st.container():
        col_rank, col_info, col_actions = st.columns([0.5, 3, 1.5])
        with col_rank:
            st.markdown(f"""
            <div style="background:{rb_bg};color:{rb_text};border-radius:12px;
                        padding:10px 6px;text-align:center;font-size:18px;font-weight:800;
                        box-shadow:0 2px 8px rgba(0,0,0,.1);min-width:50px;">
                #{rank}
            </div>
            """, unsafe_allow_html=True)
        with col_info:
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:16px 20px;
                        border-left:4px solid {score_color};box-shadow:0 3px 12px rgba(0,0,0,.05);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <h4 style="margin:0;color:#0F3D4F;font-size:16px;font-weight:800;">{type_icon} {name}</h4>
                        <p style="margin:4px 0 0;color:#7B8E96;font-size:13px;">📍 {address}</p>
                        <p style="margin:4px 0 0;color:#0F766E;font-size:12px;font-weight:600;">⏰ {eta_str}</p>
                        <p style="margin:6px 0 0;color:#4D6A75;font-size:13px;">
                            📏 {dist_km} km away &nbsp;·&nbsp;
                            <span style="background:#F0F9FF;color:#0369A1;padding:2px 8px;border-radius:6px;font-size:12px;font-weight:600;">{type_label}</span>
                        </p>
                        <div style="margin-top:8px;">{breakdown_pills}</div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <div style="background:{score_color}20;border-radius:10px;padding:8px 14px;">
                            <p style="margin:0;color:#7B8E96;font-size:11px;font-weight:600;">AI SCORE</p>
                            <p style="margin:0;color:{score_color};font-size:22px;font-weight:900;">{score:.0f}</p>
                        </div>
                    </div>
                </div>
                {('<p style="margin:8px 0 0;color:#6B7280;font-size:12px;">📞 ' + phone + '</p>') if phone else ""}
            </div>
            """, unsafe_allow_html=True)
        with col_actions:
            st.markdown("<br>", unsafe_allow_html=True)
            st.link_button("🗺️ Directions", maps_url, use_container_width=True)
            if website:
                st.link_button("🌐 Website", website, use_container_width=True)
            if st.button("⭐ Favourite", key=f"fav_btn_{facility.get('osm_id', name)}", use_container_width=True):
                if patient_email:
                    db.add_favorite(patient_email, name, address, lat, lng)
                    st.success("Saved to favourites!")
                    st.rerun()
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

def ai_best_hospital_card(facility: dict, disease: str = ""):
    """Render the M9 AI-chosen best hospital card with gold border and ETAs (Phase 4)."""
    import streamlit as st
    from utils.osm_service import get_directions_url

    name       = facility.get("name", "Best Match")
    address    = facility.get("address", "")
    dist_km    = facility.get("distance_km", 0)
    score      = facility.get("total_score", 0)
    ftype      = facility.get("type", "hospital")
    phone      = facility.get("phone", "")
    website    = facility.get("website", "")
    lat        = facility.get("lat")
    lng        = facility.get("lng")
    explanation = facility.get("ai_explanation", "")
    type_icon  = {"hospital": "🏥", "clinic": "🏨", "doctor": "👨‍⚕️"}.get(ftype.lower(), "🏥")
    maps_url   = get_directions_url(name, lat, lng)

    # ETAs
    etas = facility.get("travel_etas", {})
    drv = etas.get("driving", 0)
    wlk = etas.get("walking", 0)
    cyc = etas.get("cycling", 0)
    eta_str = f"🚗 {drv} min drive &nbsp;·&nbsp; 🚲 {cyc} min cycle &nbsp;·&nbsp; 🚶 {wlk} min walk"

    # Breakdown calculations
    bd = facility.get("score_breakdown", {})
    dist_pts = round(bd.get("distance", 0) * 0.40, 1)
    spec_pts = round(bd.get("specialty", 0) * 0.25, 1)
    type_pts = round(bd.get("type", 0) * 0.20, 1)
    phon_pts = round(bd.get("phone", 0) * 0.10, 1)
    web_pts  = round(bd.get("website", 0) * 0.05, 1)

    breakdown_pills = (
        f'<span style="background:white;color:#78350F;border:1px solid #F59E0B;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">📍 Prox: +{dist_pts}</span>'
        f'<span style="background:white;color:#047857;border:1px solid #10B981;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">🔬 Spec: +{spec_pts}</span>'
        f'<span style="background:white;color:#1D4ED8;border:1px solid #3B82F6;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">🏢 Type: +{type_pts}</span>'
        f'<span style="background:white;color:#BE123C;border:1px solid #F43F5E;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">📞 Phone: +{phon_pts}</span>'
        f'<span style="background:white;color:#6D28D9;border:1px solid #8B5CF6;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;">🌐 Web: +{web_pts}</span>'
    )

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);
                border:2px solid #F59E0B;border-radius:20px;
                padding:24px 28px;margin-bottom:20px;
                box-shadow:0 8px 25px rgba(245,158,11,0.2);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:32px;">⭐</span>
                <div>
                    <p style="margin:0;color:#92400E;font-size:12px;font-weight:700;text-transform:uppercase;">
                        🤖 AI Best Match — Recommended by Healthcare AI
                    </p>
                    <h3 style="margin:4px 0 0;color:#78350F;font-size:20px;font-weight:900;">
                        {type_icon} {name}
                    </h3>
                </div>
            </div>
            <div style="background:white;border-radius:12px;padding:10px 18px;text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,.1);">
                <p style="margin:0;color:#92400E;font-size:11px;font-weight:700;">AI SCORE</p>
                <p style="margin:0;color:#D97706;font-size:26px;font-weight:900;">{score:.0f}</p>
            </div>
        </div>
        <p style="margin:0 0 4px;color:#78350F;font-size:14px;">📍 {address} &nbsp;·&nbsp; 📏 {dist_km} km</p>
        <p style="margin:0 0 8px;color:#0F766E;font-size:13px;font-weight:600;">⏰ {eta_str}</p>
        {('<p style="margin:4px 0;color:#78350F;font-size:13px;">📞 ' + phone + '</p>') if phone else ""}
        <div style="margin:10px 0 10px 0;">{breakdown_pills}</div>
        <p style="margin:10px 0 0;color:#92400E;font-size:13px;line-height:1.5;">{explanation}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🗺️ Get Directions to Best Match", maps_url, use_container_width=True)
    with col2:
        if website:
            st.link_button("🌐 Visit Website", website, use_container_width=True)


def appointment_request_form(hospital_name: str = "", hospital_address: str = "",
                              specialty: str = "", disease: str = ""):
    """Render the Appointment Request / Personal Appointment Planner form (Phase 4 M8)."""
    import streamlit as st
    import utils.database as db
    from datetime import date, timedelta

    st.markdown("""
    <div style="background:linear-gradient(135deg,#F0F9FF,#E0F2FE);border:1px solid #7DD3FC;
                border-radius:18px;padding:20px 24px;margin-bottom:16px;">
        <h4 style="margin:0 0 4px;color:#0369A1;font-size:17px;font-weight:700;">
            📋 Personal Appointment Planner
        </h4>
        <p style="margin:0;color:#0284C7;font-size:13px;">
            ℹ️ This saves your appointment intent locally.
            <strong>Contact the hospital directly to confirm your booking.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    patient_email = st.session_state.get("user_email", "")

    with st.form("appointment_request_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            hosp_name = st.text_input("Hospital / Clinic Name", value=hospital_name,
                                       placeholder="e.g. Apollo Hospital Mumbai")
            pref_date = st.date_input("Preferred Date",
                                       min_value=date.today() + timedelta(days=1),
                                       value=date.today() + timedelta(days=3))
        with col2:
            spec_field = st.text_input("Specialty", value=specialty,
                                        placeholder="e.g. Cardiology, Endocrinology")
            pref_time = st.selectbox("Preferred Time",
                                      ["09:00 AM","10:00 AM","11:00 AM",
                                       "12:00 PM","02:00 PM","03:00 PM","04:00 PM"])

        reason = st.text_input("Reason for Visit",
                                value=f"{disease} Risk Consultation" if disease else "",
                                placeholder="e.g. Diabetes follow-up consultation")
        notes  = st.text_area("Additional Notes", placeholder="Any symptoms or concerns...", height=80)

        submitted = st.form_submit_button("📋 Save Appointment Request", use_container_width=True)

        if submitted:
            if not hosp_name.strip() or not reason.strip():
                st.error("Please fill in Hospital Name and Reason.")
            elif not patient_email:
                st.warning("Please log in to save appointment requests.")
            else:
                date_time_str = f"{pref_date} {pref_time}"
                db.create_appointment_request(
                    patient_email=patient_email,
                    doctor_name=spec_field or "Specialist",
                    date_time=date_time_str,
                    reason=reason,
                    hospital_name=hosp_name,
                    hospital_address=hospital_address,
                    specialty=spec_field,
                    appointment_type="request"
                )
                db.add_notification(patient_email,
                    f"Appointment request saved: {hosp_name} on {date_time_str} for '{reason}'.")
                st.success(f"✅ Appointment request saved for {hosp_name} on {pref_date}!")
                st.info("📌 Remember to call the hospital to confirm your slot.")


def followup_reminder_form(disease: str = ""):
    """Render medicine and follow-up reminder form (Phase 4 EX-2)."""
    import streamlit as st
    import utils.database as db
    from datetime import date, timedelta

    REMINDER_ICONS = {
        "medicine": "💊",
        "exercise": "🏃",
        "water": "💧",
        "test": "🔬",
        "consultation": "📅",
    }

    st.markdown("""
    <h4 style="margin:0 0 12px;color:#0F3D4F;font-size:15px;font-weight:600;">
        💊 Set a Health Reminder
    </h4>
    """, unsafe_allow_html=True)

    patient_email = st.session_state.get("user_email", "")

    with st.form("reminder_form", clear_on_submit=True):
        reminder_type = st.selectbox(
            "Reminder Type",
            options=list(REMINDER_ICONS.keys()),
            format_func=lambda x: f"{REMINDER_ICONS[x]} {x.capitalize()}"
        )
        message  = st.text_input("Reminder Message",
                                   placeholder="e.g. Take Metformin 500mg after breakfast")
        due_date = st.date_input("Due Date / Start Date",
                                  min_value=date.today(),
                                  value=date.today() + timedelta(days=1))
        submitted = st.form_submit_button("💾 Save Reminder", use_container_width=True)

        if submitted:
            if not message.strip():
                st.error("Please enter a reminder message.")
            elif not patient_email:
                st.warning("Please log in to save reminders.")
            else:
                db.add_followup(patient_email, disease, str(due_date), reminder_type, message)
                st.success(f"✅ {REMINDER_ICONS[reminder_type]} Reminder saved for {due_date}!")
