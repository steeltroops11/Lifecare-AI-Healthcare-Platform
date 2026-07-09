# pyrefly: ignore [missing-import]
import pytest
import time
import streamlit as st
import utils.osm_service as osm

def test_travel_etas_fallback_calculation(monkeypatch):
    # Clear ORS keys to force straight-line fallback estimation
    monkeypatch.delenv("ORS_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTESERVICE_API_KEY", raising=False)
    
    # Verify straight-line fallback duration calculations are correct
    # Dist ~3.6km -> driving: 3.6*2 + 2 = 9.2 mins (round 9), walking: 3.6*12 = 43 mins, cycle: 3.6*4 = 14 mins
    etas = osm.get_travel_etas(19.076, 72.877, 19.1, 72.9)
    assert etas["driving"] == 9
    assert etas["walking"] == 43
    assert etas["cycling"] == 14
    assert etas["from_api"] is False

def test_circuit_breaker_behavior(monkeypatch):
    # Set circuit broken unix timestamp to future
    monkeypatch.setattr(osm, "_ORS_CIRCUIT_BROKEN_UNTIL", time.time() + 100)
    
    # Call travel ETAs, should immediately bypass and return fallback without network calls
    etas = osm.get_travel_etas(19.076, 72.877, 19.1, 72.9)
    assert etas["from_api"] is False
    assert etas["driving"] == 9

def test_rate_limiter():
    if "osm_rate_limit_timestamps" in st.session_state:
        st.session_state.pop("osm_rate_limit_timestamps")
        
    # Trigger 10 requests -> should not be limited
    for _ in range(10):
        assert osm._is_rate_limited() is False
        
    # 11th request -> should be limited
    assert osm._is_rate_limited() is True
