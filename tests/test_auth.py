# pyrefly: ignore [missing-import]
import pytest
import streamlit as st
import utils.auth as auth

def test_session_initialization():
    # Streamlit session state mock is handled automatically by Streamlit packages inside tests
    auth.init_session()
    
    assert st.session_state.logged_in is False
    assert st.session_state.user_role is None
    assert st.session_state.user_email is None
    assert st.session_state.page == "Dashboard"

def test_session_logout(monkeypatch):
    st.session_state.logged_in = True
    st.session_state.user_role = "Patient"
    st.session_state.user_email = "test@test.com"
    st.session_state.user_name = "Test Name"
    st.session_state.page = "Settings"
    
    # Mock streamlit rerun since it raises an exception or does nothing in test environment
    monkeypatch.setattr(st, "rerun", lambda: None)
    
    auth.logout()
    
    assert st.session_state.logged_in is False
    assert st.session_state.user_role is None
    assert st.session_state.user_email is None
