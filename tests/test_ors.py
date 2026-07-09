# pyrefly: ignore [missing-import]
import pytest
import time
import json
import os
import urllib.request
from unittest.mock import MagicMock
import utils.ors_service as ors
import utils.osm_service as osm

def test_ors_missing_key(monkeypatch):
    # Clear key env variables
    monkeypatch.delenv("ORS_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTESERVICE_API_KEY", raising=False)
    
    res = ors.get_travel_times(19.076, 72.877, 19.1, 72.9)
    assert res["from_api"] is False
    assert res["driving_minutes"] == 9
    assert res["walking_minutes"] == 43
    assert res["cycling_minutes"] == 14

def test_ors_success(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "mock-ors-key-12345")
    
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({
        "features": [{
            "properties": {
                "summary": {
                    "duration": 600.0  # 10 minutes
                }
            }
        }]
    }).encode('utf-8')
    mock_resp.__enter__.return_value = mock_resp
    
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: mock_resp)
    
    res = ors.get_travel_times(19.076, 72.877, 19.1, 72.9)
    assert res["from_api"] is True
    assert res["driving_minutes"] == 10
    assert res["walking_minutes"] == 60
    assert res["cycling_minutes"] == 20

def test_ors_retry_success(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "mock-ors-key-12345")
    
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({
        "features": [{
            "properties": {
                "summary": {
                    "duration": 600.0
                }
            }
        }]
    }).encode('utf-8')
    mock_resp.__enter__.return_value = mock_resp
    
    call_count = 0
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Transient network failure")
        return mock_resp
        
    monkeypatch.setattr(urllib.request, "urlopen", side_effect)
    monkeypatch.setattr(time, "sleep", lambda x: None)  # Prevent sleeping 1s in test
    
    res = ors.get_travel_times(19.076, 72.877, 19.1, 72.9)
    assert res["from_api"] is True
    assert res["driving_minutes"] == 10
    assert call_count == 2

def test_ors_api_failure_trips_circuit_breaker(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "mock-ors-key-12345")
    
    # Ensure circuit breaker is not already broken
    monkeypatch.setattr(osm, "_ORS_CIRCUIT_BROKEN_UNTIL", 0.0)
    
    def side_effect(*args, **kwargs):
        raise Exception("Fatal API failure")
        
    monkeypatch.setattr(urllib.request, "urlopen", side_effect)
    monkeypatch.setattr(time, "sleep", lambda x: None)
    
    # Use osm.get_travel_etas to trigger the circuit breaker check and trip logic
    etas = osm.get_travel_etas(19.076, 72.877, 19.1, 72.9)
    
    assert etas["from_api"] is False
    assert etas["driving"] == 9
    assert osm._ORS_CIRCUIT_BROKEN_UNTIL > time.time()

def test_ors_circuit_breaker_bypasses_network(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "mock-ors-key-12345")
    
    # Set circuit breaker in future
    monkeypatch.setattr(osm, "_ORS_CIRCUIT_BROKEN_UNTIL", time.time() + 300)
    
    def side_effect(*args, **kwargs):
        pytest.fail("Network should not be called when circuit is broken")
        
    monkeypatch.setattr(urllib.request, "urlopen", side_effect)
    
    etas = osm.get_travel_etas(19.076, 72.877, 19.1, 72.9)
    assert etas["from_api"] is False
    assert etas["driving"] == 9
