# PDF Report Generator & Medical Data with Premium Layout (Priority 7)
import streamlit as st
import pandas as pd
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from utils.logger import get_logger

logger = get_logger("utils.pdf_generator")

# -----------------------------
# CORE DATA DICTIONARIES
# -----------------------------
medical_history = {
    "Diabetes": {
        "Diabetes Management": ["Diabetes Control", "Blood Glucose Monitoring", "HbA1c Tracking"],
        "Related Conditions": ["Diabetic Neuropathy", "Diabetic Retinopathy", "Diabetic Nephropathy"],
        "Medications": ["Metformin", "Insulin", "Other Antidiabetics"],
        "Follow-up": ["Endocrinologist Visit", "Eye Exam", "Kidney Function Test"]
    },
    "Heart Disease": {
        "Cardiovascular Health": ["Blood Pressure Monitoring", "Cholesterol Monitoring", "Heart Rate Monitoring"],
        "Related Conditions": ["Hypertension", "Coronary Artery Disease", "Heart Failure"],
        "Medications": ["Statins", "Antihypertensives", "Antiplatelets"],
        "Follow-up": ["Cardiologist Visit", "ECG", "Echocardiogram"]
    },
    "Kidney Disease": {
        "Renal Function": ["Blood Pressure Monitoring", "Blood Urea Monitoring", "Serum Creatinine Monitoring"],
        "Related Conditions": ["Hypertension", "Diabetes", "CKD Stages"],
        "Medications": ["ACE Inhibitors", "Diuretics", "Electrolyte Supplements"],
        "Follow-up": ["Nephrologist Visit", "Kidney Function Tests", "Urine Analysis"]
    },
    "Readmission": {
        "Hospital Utilization": ["Hospitalization History", "ER Visits", "Outpatient Visits"],
        "Medication Management": ["Medication Adherence", "Medication Reconciliation", "Pharmacy Records"],
        "Health Monitoring": ["Vital Signs Monitoring", "Symptom Tracking", "Follow-up Schedule"],
        "Social Support": ["Family Support", "Home Care Services", "Community Health Resources"]
    }
}

recommendations = {
    "Diabetes": [
        "Walk 30-45 minutes daily",
        "Limit sugary drinks and sweets",
        "Consume high-fiber foods",
        "Monitor fasting blood glucose regularly",
        "Maintain BMI between 18.5 and 24.9",
        "Sleep 7-8 hours daily",
        "Schedule endocrinology follow-ups"
    ],
    "Heart Disease": [
        "Perform 150 minutes of exercise weekly",
        "Reduce saturated fat intake",
        "Monitor blood pressure weekly",
        "Maintain healthy cholesterol levels",
        "Avoid smoking and tobacco products",
        "Practice stress management",
        "Schedule cardiovascular evaluations"
    ],
    "Kidney Disease": [
        "Reduce sodium intake",
        "Maintain proper hydration",
        "Monitor blood pressure regularly",
        "Avoid unnecessary painkillers",
        "Monitor kidney function tests",
        "Follow nephrologist recommendations",
        "Maintain a kidney-friendly diet"
    ],
    "Readmission": [
        "Attend all follow-up appointments",
        "Take medications consistently",
        "Monitor symptoms regularly",
        "Follow discharge instructions carefully",
        "Maintain communication with physicians",
        "Track medication schedules",
        "Seek help immediately if symptoms worsen"
    ]
}

def display_medical_history(disease_type):
    if disease_type not in medical_history:
        st.warning("No medical history data available for this condition.")
        return

    st.subheader("Detailed Medical History")
    categories = medical_history[disease_type]

    for category, items in categories.items():
        df = pd.DataFrame({
            "Category": [category] * len(items),
            "Medical Fields": items
        })
        st.table(df)

# Helper to construct header table representing a hospital logo + branding
def get_pdf_header(styles):
    header_data = [
        [
            Paragraph("<b>🏥 LIFECARE ANALYTICS HOSPITAL</b><br/>"
                      "<font size=8 color='#7B8E96'>AI-Powered Clinical Diagnostics Center<br/>"
                      "100 Medical Parkway, Suite 500 | Tel: (555) 019-2834</font>", styles["Normal"]),
            Paragraph("<para align='right'><font size=9 color='#0F6E84'><b>DIGITAL REPORT VERIFICATION</b><br/>"
                      "Secure EHR Integration System</font></para>", styles["Normal"])
        ]
    ]
    header_table = Table(header_data, colWidths=[280, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 1, HexColor('#0F6E84')),
    ]))
    return header_table

# Helper to build a styled patient information table card (ID, Name, Age, Blood Group, Emergency Contact)
def get_patient_summary_table(styles):
    # Fetch active user details from state
    name = st.session_state.get("user_name") or "N/A"
    email = st.session_state.get("user_email") or "N/A"
    role = st.session_state.get("user_role") or "Patient"
    
    # Check if there is profile details in DB
    import utils.database as db
    user_info = db.get_user(email) if email != "N/A" else None
    
    p_id = (user_info.get("patient_id") or "N-10928") if user_info else "N-10928"
    age = str(user_info.get("age") or 35) if user_info else "35"
    blood = (user_info.get("blood_group") or "O+") if user_info else "O+"
    emergency = (user_info.get("emergency_contact") or "+1 (555) 019-9234") if user_info else "+1 (555) 019-9234"
    
    info_data = [
        [Paragraph("<b>Patient Name:</b>", styles["Normal"]), Paragraph(name, styles["Normal"]),
         Paragraph("<b>Patient ID:</b>", styles["Normal"]), Paragraph(p_id, styles["Normal"])],
        [Paragraph("<b>Age:</b>", styles["Normal"]), Paragraph(f"{age} Years", styles["Normal"]),
         Paragraph("<b>Blood Group:</b>", styles["Normal"]), Paragraph(blood, styles["Normal"])],
        [Paragraph("<b>Email:</b>", styles["Normal"]), Paragraph(email, styles["Normal"]),
         Paragraph("<b>Emerg. Contact:</b>", styles["Normal"]), Paragraph(emergency, styles["Normal"])]
    ]
    
    info_table = Table(info_data, colWidths=[90, 160, 90, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor('#F4FBFD')),
        ('BOX', (0,0), (-1,-1), 1, HexColor('#D5EAF1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('INNERGRID', (0,0), (-1,-1), 0.5, HexColor('#E8F0F3')),
    ]))
    return info_table

# Helper to build a risk bar visual representation
def get_risk_bar_table(risk_val, styles):
    risk_percent = risk_val * 100
    bar_color = '#22C55E' if risk_percent < 40 else ('#F59E0B' if risk_percent < 70 else '#EF4444')
    status_text = 'LOW RISK' if risk_percent < 40 else ('MODERATE RISK' if risk_percent < 70 else 'CRITICAL RISK')
    
    bar_data = [
        [
            Paragraph(f"<b>RISK INDEX:</b> {risk_percent:.1f}% ({status_text})", styles["Normal"]),
            Paragraph(f"<font color='{bar_color}'>■■■■■■■■■■</font>", styles["Normal"]) # Stylized representation
        ]
    ]
    bar_table = Table(bar_data, colWidths=[250, 250])
    bar_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor('#FFFBEB') if risk_percent >= 40 else HexColor('#F0FDF4')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, HexColor('#F59E0B') if risk_percent >= 40 else HexColor('#22C55E')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
    ]))
    return bar_table

# Helper for doctor signature block + QR verification block
def get_signatures_block(styles):
    # Mock signature drawing table
    sig_data = [
        [
            Paragraph("<b>REPORT QR CODE VERIFICATION:</b><br/>"
                      "<font size=7 color='gray'>Scan QR to verify clinical report authenticity with the Lifecare EHR blockchain ledger.</font>", styles["Normal"]),
            Paragraph("<br/>_____________________________________<br/><b>Dr. Navish M.D.</b><br/><font size=8 color='gray'>Chief Medical Officer, Lifecare</font>", styles["Normal"])
        ]
    ]
    
    # We can represent a QR code via a small square cell with border in the signature block
    sig_table = Table(sig_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    return sig_table

def generate_pdf_report(reports, overall_risk, specialist_set, recs=None):
    if recs is None:
        recs = recommendations

    os.makedirs("reports", exist_ok=True)
    pdf_path = "reports/Healthcare_Report.pdf"
    logger.info(f"[PDF_GEN_COMBINED_START] count='{len(reports)}' pdf_path='{pdf_path}'")
    doc = SimpleDocTemplate(pdf_path, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    
    # Custom heading styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=HexColor('#0F3D4F'),
        spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name='CustomHeading',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=HexColor('#0F6E84'),
        spaceBefore=12,
        spaceAfter=6
    ))

    content = []

    # 1. Header (Branding & Logo layout)
    content.append(get_pdf_header(styles))
    content.append(Spacer(1, 15))

    # Title
    content.append(Paragraph("Comprehensive Patient Risk Assessment Report", styles["CustomTitle"]))

    # 2. Patient Summary
    content.append(Paragraph("PATIENT CLINICAL SUMMARY", styles["CustomHeading"]))
    content.append(get_patient_summary_table(styles))
    content.append(Spacer(1, 15))

    # 3. Overall Risk Bar
    content.append(Paragraph("OVERALL SYSTEM METRIC RISK INDEX", styles["CustomHeading"]))
    content.append(get_risk_bar_table(overall_risk / 100, styles))
    content.append(Spacer(1, 15))

    # 4. Disease Risk Table
    content.append(Paragraph("ML-CLASSIFIER SCREENING ASSESSMENTS", styles["CustomHeading"]))
    
    table_rows = [[Paragraph("<b>Screening Disease</b>", styles["Normal"]), 
                   Paragraph("<b>Calculated Risk</b>", styles["Normal"]), 
                   Paragraph("<b>Clinical Specialist Assignment</b>", styles["Normal"])]]
    
    specialists_map = {
        "Diabetes": "Endocrinologist",
        "Heart Disease": "Cardiologist",
        "Kidney Disease": "Nephrologist",
        "Readmission": "Care Transition Coordinator"
    }

    for disease, data in reports.items():
        risk = data["risk"] * 100
        specialist = specialists_map.get(disease, "Physician")
        table_rows.append([
            Paragraph(disease, styles["Normal"]),
            Paragraph(f"{risk:.2f}%", styles["Normal"]),
            Paragraph(specialist, styles["Normal"])
        ])

    disease_table = Table(table_rows, colWidths=[200, 100, 200])
    disease_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#0F6E84')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#E8F0F3')),
    ]))
    content.append(disease_table)
    content.append(Spacer(1, 15))

    # 5. Lifestyle & Treatment Recommendations
    content.append(Paragraph("PREVENTATIVE CARE LIFESTYLE RECOMMENDATIONS", styles["CustomHeading"]))
    for disease in reports.keys():
        content.append(Paragraph(f"<b>{disease} Preventative Actions:</b>", styles["Normal"]))
        for item in recs.get(disease, []):
            content.append(Paragraph(f"• {item}", styles["Normal"]))
        content.append(Spacer(1, 6))
    content.append(Spacer(1, 15))

    # 6. Signatures & Blockchain Verification Footer
    content.append(get_signatures_block(styles))

    try:
        doc.build(content)
    except Exception as e:
        logger.error(f"[PDF_GEN_FAIL] error='{str(e)}'", exc_info=True)
        raise
    logger.info(f"[PDF_GEN_COMBINED_SUCCESS] pdf_path='{pdf_path}'")
    return pdf_path


def generate_single_report_pdf(disease, risk, prediction, recs_list):
    """Generate a premium clinical PDF report for a single disease prediction."""
    os.makedirs("reports", exist_ok=True)
    pdf_path = f"reports/{disease.replace(' ', '_')}_Report.pdf"
    logger.info(f"[PDF_GEN_SINGLE_START] disease='{disease}' pdf_path='{pdf_path}'")
    doc = SimpleDocTemplate(pdf_path, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    
    # Custom heading styles
    styles.add(ParagraphStyle(
        name='CustomTitleSingle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=HexColor('#0F3D4F'),
        spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name='CustomHeadingSingle',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=HexColor('#0F6E84'),
        spaceBefore=12,
        spaceAfter=6
    ))

    content = []

    # 1. Header
    content.append(get_pdf_header(styles))
    content.append(Spacer(1, 15))

    # Title
    content.append(Paragraph(f"{disease} Diagnostic Screening Report", styles["CustomTitleSingle"]))

    # 2. Patient Summary
    content.append(Paragraph("PATIENT DETAILS", styles["CustomHeadingSingle"]))
    content.append(get_patient_summary_table(styles))
    content.append(Spacer(1, 15))

    # 3. Risk index gauge table
    content.append(Paragraph("DIAGNOSTIC SCREENING METRICS", styles["CustomHeadingSingle"]))
    content.append(get_risk_bar_table(risk, styles))
    content.append(Spacer(1, 15))

    # 4. Lifestyle & Treatment Recommendations
    content.append(Paragraph("RECOMMENDED CARE ACTIONS", styles["CustomHeadingSingle"]))
    for item in recs_list:
        content.append(Paragraph(f"• {item}", styles["Normal"]))
    content.append(Spacer(1, 20))

    # 5. Signatures
    content.append(get_signatures_block(styles))

    try:
        doc.build(content)
    except Exception as e:
        logger.error(f"[PDF_GEN_FAIL] error='{str(e)}'", exc_info=True)
        raise
    logger.info(f"[PDF_GEN_SINGLE_SUCCESS] pdf_path='{pdf_path}'")
    return pdf_path
