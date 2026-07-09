# Phase 4 — AI Clinical Recommendation Engine
# Rule-based logic. No API required.
# Returns a structured RecommendationObject that feeds disease pages, dashboard, PDF, chatbot.

# ─────────────────────────────────────────────
# DISEASE → SPECIALIST MAPPING
# ─────────────────────────────────────────────
DISEASE_SPECIALIST_MAP = {
    "Diabetes": {
        "specialist": "Endocrinologist",
        "department": "Endocrinology & Metabolics",
        "emergency_dept": "General Medicine",
        "keywords": ["diabetes", "endocrine", "endocrinology", "metabolic", "thyroid", "sugar"],
    },
    "Heart Disease": {
        "specialist": "Cardiologist",
        "department": "Cardiology & Cardiovascular Surgery",
        "emergency_dept": "Cardiology",
        "keywords": ["heart", "cardiac", "cardio", "cardiovascular", "cardiology"],
    },
    "Kidney Disease": {
        "specialist": "Nephrologist",
        "department": "Nephrology & Renal Medicine",
        "emergency_dept": "Nephrology",
        "keywords": ["kidney", "renal", "nephro", "nephrology", "dialysis"],
    },
    "Readmission": {
        "specialist": "General Physician",
        "department": "Internal Medicine & Care Transitions",
        "emergency_dept": "General Medicine",
        "keywords": ["general", "medicine", "multispeciality", "hospital", "clinic"],
    },
}

# ─────────────────────────────────────────────
# RISK TIER THRESHOLDS
# ─────────────────────────────────────────────
def _get_risk_tier(risk_pct: float) -> dict:
    """Return risk tier metadata for a given percentage (0–100)."""
    if risk_pct < 35:
        return {
            "risk_level": "LOW",
            "risk_color": "#22C55E",
            "risk_bg": "#F0FDF4",
            "risk_emoji": "🟢",
            "urgency": "No doctor visit required",
            "urgency_days": None,
            "emergency": False,
            "followup": "3 months",
        }
    elif risk_pct < 60:
        return {
            "risk_level": "MODERATE",
            "risk_color": "#F59E0B",
            "risk_bg": "#FFFBEB",
            "risk_emoji": "🟡",
            "urgency": "Visit a General Physician within 30 days",
            "urgency_days": 30,
            "emergency": False,
            "followup": "1 month",
        }
    elif risk_pct < 80:
        return {
            "risk_level": "HIGH",
            "risk_color": "#F97316",
            "risk_bg": "#FFF7ED",
            "risk_emoji": "🟠",
            "urgency": "Consult a Specialist within 7 days",
            "urgency_days": 7,
            "emergency": False,
            "followup": "2 weeks",
        }
    else:
        return {
            "risk_level": "CRITICAL",
            "risk_color": "#EF4444",
            "risk_bg": "#FEF2F2",
            "risk_emoji": "🔴",
            "urgency": "Seek emergency care within 2 hours",
            "urgency_days": 0,
            "emergency": True,
            "followup": "48 hours",
        }


# ─────────────────────────────────────────────
# DIABETES RULES
# ─────────────────────────────────────────────
def _diabetes_rules(risk_pct, inputs):
    glucose  = inputs.get("glucose", 120)
    bmi      = inputs.get("bmi", 25.0)
    insulin  = inputs.get("insulin", 80)
    age      = inputs.get("age", 30)
    dpf      = inputs.get("dpf", 0.5)

    tests = ["Fasting Blood Glucose"]
    if glucose > 125:
        tests.append("HbA1c (Glycated Haemoglobin)")
    if insulin > 200:
        tests.append("Serum Insulin Level")
    if age > 45:
        tests.append("Oral Glucose Tolerance Test (OGTT)")
    if risk_pct > 50:
        tests.append("Lipid Profile")
    if risk_pct > 70:
        tests.append("Kidney Function Test (early nephropathy check)")

    immediate = []
    if glucose > 180:
        immediate.append("✔ Reduce sugar intake immediately")
    if bmi >= 25:
        immediate.append("✔ Walk 30 mins daily")
    immediate.append("✔ Monitor fasting glucose every morning")
    if risk_pct > 60:
        immediate.append("✔ Schedule Endocrinologist consultation")
    if glucose > 125:
        immediate.append("✔ Get HbA1c tested this week")

    emergency_msg = ""
    if risk_pct > 85 and glucose > 250:
        emergency_msg = "⚠️ Critically high glucose detected. Proceed to the nearest hospital Emergency department NOW. Call 108."

    return tests, immediate, emergency_msg


# ─────────────────────────────────────────────
# HEART DISEASE RULES
# ─────────────────────────────────────────────
def _heart_rules(risk_pct, inputs):
    trestbps = inputs.get("trestbps", 120)
    chol     = inputs.get("chol", 200)
    age      = inputs.get("age", 50)
    exang    = inputs.get("exang", 0)

    tests = ["Blood Pressure Monitoring"]
    if chol > 200:
        tests.append("Fasting Lipid Profile")
    if risk_pct > 60:
        tests.append("Resting ECG (Electrocardiogram)")
    if risk_pct > 75:
        tests.append("Stress Test (Treadmill/Exercise ECG)")
    if risk_pct > 80:
        tests.append("Echocardiogram")
        tests.append("Troponin Blood Test")

    immediate = []
    if trestbps > 140:
        immediate.append("✔ Monitor blood pressure twice daily")
    if chol > 200:
        immediate.append("✔ Reduce saturated fats (butter, red meat)")
    immediate.append("✔ Perform 150 mins of moderate exercise weekly")
    if risk_pct > 70:
        immediate.append("✔ Avoid strenuous physical activity until evaluated")
    if risk_pct > 60:
        immediate.append("✔ Schedule Cardiologist consultation")
        immediate.append("✔ Get ECG and Lipid Profile done")

    emergency_msg = ""
    if risk_pct > 85:
        emergency_msg = "🚨 CARDIAC EMERGENCY: Chest pain or shortness of breath requires IMMEDIATE medical attention. Call 108 now. Do NOT drive yourself to hospital."

    return tests, immediate, emergency_msg


# ─────────────────────────────────────────────
# KIDNEY DISEASE RULES
# ─────────────────────────────────────────────
def _kidney_rules(risk_pct, inputs):
    sc  = inputs.get("sc", 1.2)   # serum creatinine
    bu  = inputs.get("bu", 40)    # blood urea
    bp  = inputs.get("bp", 80)
    hemo = inputs.get("hemo", 15.0)

    tests = ["Serum Creatinine"]
    tests.append("Blood Urea Nitrogen (BUN)")
    if risk_pct > 50:
        tests.append("eGFR (Estimated Glomerular Filtration Rate)")
        tests.append("Urine Routine & Microscopy")
    if risk_pct > 70:
        tests.append("24-hour Urine Protein")
        tests.append("Renal Ultrasound")
    if hemo < 12:
        tests.append("Complete Blood Count (Anaemia check)")

    immediate = []
    immediate.append("✔ Reduce sodium (salt) intake")
    immediate.append("✔ Drink 2.5L of water daily")
    immediate.append("✔ Avoid NSAIDs (Ibuprofen, Aspirin) unless prescribed")
    if bp > 90:
        immediate.append("✔ Monitor and control blood pressure")
    if risk_pct > 60:
        immediate.append("✔ Schedule Nephrologist consultation")
        immediate.append("✔ Follow low-protein diet (limit red meat)")

    emergency_msg = ""
    if risk_pct > 90:
        emergency_msg = "🚨 CRITICAL RENAL FAILURE RISK: Proceed immediately to hospital. Dialysis evaluation may be required. Call 108."

    return tests, immediate, emergency_msg


# ─────────────────────────────────────────────
# READMISSION RULES
# ─────────────────────────────────────────────
def _readmission_rules(risk_pct, inputs):
    num_meds      = inputs.get("num_medications", 15)
    num_inpatient = inputs.get("number_inpatient", 0)
    num_emergency = inputs.get("number_emergency", 0)

    tests = ["Medication Reconciliation Review"]
    if risk_pct > 50:
        tests.append("Vital Signs Monitoring")
        tests.append("Post-discharge Follow-up Lab Panel")
    if risk_pct > 70:
        tests.append("Social & Home Care Assessment")

    immediate = []
    immediate.append("✔ Attend all scheduled follow-up appointments")
    immediate.append("✔ Take medications exactly as prescribed")
    if num_meds > 10:
        immediate.append("✔ Use a pill organizer or medication tracker app")
    if num_inpatient + num_emergency > 3:
        immediate.append("✔ Enrol in a Care Coordination programme")
    immediate.append("✔ Contact GP immediately if symptoms worsen")

    emergency_msg = ""
    if risk_pct > 85:
        emergency_msg = "⚠️ Very high re-hospitalisation risk detected. Contact your Care Coordinator or GP within 24 hours. Do not delay."

    return tests, immediate, emergency_msg


# ─────────────────────────────────────────────
# LIFESTYLE PLAN GENERATOR
# ─────────────────────────────────────────────
def get_lifestyle_plan(disease, risk_pct, bmi=25.0, smoking="Non-smoker", alcohol="Occasional", age=30):
    """Return a personalised lifestyle plan list."""
    plan = []

    # Smoking — always top priority
    if smoking and smoking.lower() not in ["non-smoker", "never", "no", "none"]:
        plan.append("🚭 Stop smoking — reduces cardiovascular & cancer risk by up to 50%")

    # Weight
    if bmi >= 30:
        plan.append("⚖️ Target 5–10% weight loss — significantly reduces disease risk")
    elif bmi >= 25:
        plan.append("⚖️ Aim for a healthy BMI (18.5–24.9) through diet & exercise")

    # Alcohol
    if alcohol and alcohol.lower() in ["heavy", "regular", "daily", "frequent"]:
        plan.append("🍺 Limit alcohol to 1 unit/day (men) or 0.5 units/day (women)")

    # Age
    if age > 60:
        plan.append("🧓 Schedule an annual comprehensive health check-up")

    # Disease-specific
    if disease == "Diabetes":
        plan.extend([
            "🥗 Follow a low-GI diet (whole grains, vegetables, legumes)",
            "🚶 Walk 30–45 minutes daily",
            "💧 Drink 8–10 glasses of water daily",
            "🍬 Eliminate sugary drinks, sweets, and white rice",
        ])
    elif disease == "Heart Disease":
        plan.extend([
            "🫀 Follow the DASH diet (low sodium, high potassium)",
            "🏃 150 minutes of moderate aerobic exercise per week",
            "🧂 Limit sodium to < 2,300 mg/day",
            "🐟 Eat omega-3 rich foods (salmon, walnuts, flaxseed)",
        ])
    elif disease == "Kidney Disease":
        plan.extend([
            "🧂 Restrict sodium to < 2,000 mg/day",
            "💧 Maintain hydration — 2.5L of water daily",
            "🥩 Limit protein intake (avoid excess red meat)",
            "💊 Never self-medicate with painkillers (NSAIDs)",
        ])
    elif disease == "Readmission":
        plan.extend([
            "📋 Follow your discharge instructions precisely",
            "💊 Maintain a strict medication schedule",
            "📞 Call your GP if any symptom changes",
            "🏠 Arrange home care support if living alone",
        ])

    if risk_pct >= 60:
        plan.append("😴 Prioritise 7–8 hours of quality sleep per night")
        plan.append("🧘 Practice stress reduction (meditation, yoga, deep breathing)")

    return plan


# ─────────────────────────────────────────────
# DYNAMIC EXPLANATION GENERATOR
# ─────────────────────────────────────────────
def generate_ai_explanation(disease, risk_pct, patient_data, inputs, risk_tier):
    """Generate a personalised natural-language explanation of the risk."""
    age     = patient_data.get("age") or inputs.get("age", 30)
    smoking = patient_data.get("smoking", "Non-smoker")
    bmi_val = None
    w = patient_data.get("weight_kg")
    h = patient_data.get("height_cm")
    if w and h:
        bmi_val = round(w / ((h / 100) ** 2), 1)
    family  = patient_data.get("family_history", "None")
    level   = risk_tier["risk_level"]

    parts = [f"Based on the clinical parameters provided, the AI model calculates a {risk_pct:.1f}% risk score, classified as {level}."]

    if disease == "Diabetes":
        glucose = inputs.get("glucose", 120)
        bmi_in  = inputs.get("bmi", bmi_val or 25.0)
        parts.append(f"Plasma glucose of {glucose} mg/dL {'is significantly elevated' if glucose > 125 else 'is within borderline range'}.")
        if bmi_in >= 30:
            parts.append(f"BMI of {bmi_in:.1f} falls in the obese range, which substantially increases insulin resistance.")
        if smoking and "non" not in smoking.lower():
            parts.append("Active smoking further impairs glucose metabolism.")
        if "diabetes" in family.lower():
            parts.append("Family history of Diabetes increases genetic predisposition.")

    elif disease == "Heart Disease":
        trestbps = inputs.get("trestbps", 120)
        chol     = inputs.get("chol", 200)
        parts.append(f"Resting blood pressure of {trestbps} mmHg is {'hypertensive' if trestbps > 140 else 'pre-hypertensive' if trestbps > 120 else 'optimal'}.")
        parts.append(f"Serum cholesterol of {chol} mg/dL is {'high' if chol > 240 else 'borderline high' if chol > 200 else 'desirable'}.")
        if smoking and "non" not in smoking.lower():
            parts.append(f"At age {age}, active smoking critically elevates cardiovascular risk.")
        if "heart" in family.lower() or "cardiac" in family.lower():
            parts.append("Family history of heart disease increases inherited risk.")

    elif disease == "Kidney Disease":
        sc = inputs.get("sc", 1.2)
        bu = inputs.get("bu", 40)
        parts.append(f"Serum creatinine of {sc} mg/dL is {'severely elevated — indicates impaired kidney filtration' if sc > 2.0 else 'elevated' if sc > 1.2 else 'within normal range'}.")
        parts.append(f"Blood urea of {bu} mg/dL {'indicates significant renal load' if bu > 60 else 'is borderline'}.")

    elif disease == "Readmission":
        num_in = inputs.get("number_inpatient", 0)
        num_em = inputs.get("number_emergency", 0)
        t_days = inputs.get("time_in_hospital", 4)
        parts.append(f"Patient had {num_in} inpatient stays and {num_em} emergency visits in the past year.")
        parts.append(f"A hospital stay of {t_days} days with {inputs.get('num_medications', 15)} active medications increases care complexity.")

    parts.append(f"Action required: {risk_tier['urgency']}.")
    return " ".join(parts)


# ─────────────────────────────────────────────
# CONTEXT RISK AMPLIFIER (M4)
# ─────────────────────────────────────────────
def _amplify_risk(disease, risk_pct, patient_data):
    """Apply patient context escalation rules to effective risk tier."""
    effective = risk_pct
    age     = patient_data.get("age") or 30
    smoking = (patient_data.get("smoking") or "").lower()
    family  = (patient_data.get("family_history") or "").lower()
    prev_d  = (patient_data.get("prev_diseases") or "").lower()
    w = patient_data.get("weight_kg")
    h = patient_data.get("height_cm")
    bmi_val = (w / ((h / 100) ** 2)) if w and h else None

    # Smoker + Heart risk > 70% → escalate to CRITICAL (80+)
    if disease == "Heart Disease" and risk_pct > 70 and "non" not in smoking and smoking != "":
        effective = max(effective, 82)

    # Age > 60 + any HIGH risk → escalate one tier
    if age > 60 and risk_pct >= 60:
        effective = min(effective + 8, 99)

    # Family history of same disease → add 5 pts to effective
    disease_lower = disease.lower().replace(" disease", "").replace(" ", "")
    if any(kw in family for kw in [disease_lower, "diabetes", "heart", "kidney", "cardiac"]):
        effective = min(effective + 5, 99)

    # BMI > 35 + Diabetes risk > 50% → escalate to HIGH
    if disease == "Diabetes" and bmi_val and bmi_val > 35 and risk_pct > 50:
        effective = max(effective, 62)

    # Previous same disease → always at least MODERATE
    if disease_lower in prev_d:
        effective = max(effective, 40)

    return effective


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────
def get_recommendation(disease: str, risk: float, patient_data: dict, inputs: dict) -> dict:
    """
    Main recommendation engine.
    Returns a RecommendationObject dict with all clinical guidance fields.

    Args:
        disease:      "Diabetes" | "Heart Disease" | "Kidney Disease" | "Readmission"
        risk:         float 0.0–1.0 (model probability)
        patient_data: dict from db.get_user()
        inputs:       dict of clinical inputs used for prediction

    Returns:
        RecommendationObject dict
    """
    risk_pct = risk * 100

    # Apply patient context amplifiers
    effective_risk = _amplify_risk(disease, risk_pct, patient_data)

    # Get risk tier based on effective (context-adjusted) risk
    tier = _get_risk_tier(effective_risk)

    # Disease-specific rules
    if disease == "Diabetes":
        tests, immediate, emergency_msg = _diabetes_rules(risk_pct, inputs)
    elif disease == "Heart Disease":
        tests, immediate, emergency_msg = _heart_rules(risk_pct, inputs)
    elif disease == "Kidney Disease":
        tests, immediate, emergency_msg = _kidney_rules(risk_pct, inputs)
    else:
        tests, immediate, emergency_msg = _readmission_rules(risk_pct, inputs)

    # Override emergency message if CRITICAL
    if tier["emergency"] and not emergency_msg:
        emergency_msg = f"⚠️ CRITICAL RISK: Seek emergency medical care immediately. Call 108."

    # Specialist info
    spec_info = DISEASE_SPECIALIST_MAP.get(disease, DISEASE_SPECIALIST_MAP["Readmission"])

    # Lifestyle plan
    smoking = patient_data.get("smoking", "Non-smoker")
    alcohol = patient_data.get("alcohol", "Occasional")
    age = patient_data.get("age") or inputs.get("age", 30)
    w = patient_data.get("weight_kg")
    h = patient_data.get("height_cm")
    bmi_for_plan = (w / ((h / 100) ** 2)) if w and h else inputs.get("bmi", 25.0)
    lifestyle = get_lifestyle_plan(disease, risk_pct, bmi_for_plan, smoking, alcohol, age)

    # Dynamic explanation
    explanation = generate_ai_explanation(disease, risk_pct, patient_data, inputs, tier)

    # Build the RecommendationObject
    rec = {
        # Risk classification
        "risk_level":        tier["risk_level"],
        "risk_color":        tier["risk_color"],
        "risk_bg":           tier["risk_bg"],
        "risk_emoji":        tier["risk_emoji"],
        "effective_risk":    effective_risk,

        # Urgency
        "urgency":           tier["urgency"],
        "urgency_days":      tier["urgency_days"],
        "followup":          tier["followup"],

        # Emergency
        "emergency":         tier["emergency"],
        "emergency_msg":     emergency_msg,

        # Specialist
        "doctor":            spec_info["specialist"],
        "specialist":        spec_info["specialist"],
        "department":        spec_info["department"],
        "emergency_dept":    spec_info["emergency_dept"],
        "specialty_keywords": spec_info["keywords"],

        # Clinical guidance
        "tests":             tests,
        "lifestyle":         lifestyle,
        "immediate_actions": immediate,

        # Narrative
        "explanation":       explanation,
    }

    return rec
