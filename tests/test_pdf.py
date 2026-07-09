# pyrefly: ignore [missing-import]
import pytest
import os
import streamlit as st
from utils.pdf_generator import generate_single_report_pdf

def test_pdf_generation():
    # Initialize session state mock variables to prevent test pollution
    st.session_state["user_name"] = "John Doe"
    st.session_state["user_email"] = "patient@healthcare.com"
    st.session_state["user_role"] = "Patient"

    os.makedirs("reports", exist_ok=True)
    pdf_path = "reports/Diabetes_Report.pdf"
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        
    generate_single_report_pdf(
        disease="Diabetes",
        risk=0.83,
        prediction=1,
        recs_list=["HbA1c Tracking"]
    )
    
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0
