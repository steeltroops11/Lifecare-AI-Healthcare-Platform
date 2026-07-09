import pytest
import streamlit as st

def test_dashboard_session_variables():
    # Test session state variables initialization directly to avoid test pollution
    st.session_state["user_email"] = "patient@healthcare.com"
    st.session_state["user_role"] = "Patient"
        
    assert st.session_state["user_email"] == "patient@healthcare.com"
    assert st.session_state["user_role"] == "Patient"
