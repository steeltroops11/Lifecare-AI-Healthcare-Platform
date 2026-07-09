import pytest
from utils.hospital_ranker import rank_hospitals, get_ai_best_pick, haversine_km

def test_haversine_distance():
    # Mumbai coordinates
    dist = haversine_km(19.076, 72.877, 19.085, 72.885)
    assert round(dist, 1) == 1.3  # km

def test_ranking_algorithm_weights():
    # Test facilities
    facilities = [
        {
            "name": "Cardiology Clinic", "type": "clinic", "lat": 19.08, "lng": 72.88,
            "phone": "+91-22-12345", "website": "https://cardiocare.com", "address": "Mumbai",
            "specialty_score": 40, "osm_id": "c1"
        },
        {
            "name": "General Hospital", "type": "hospital", "lat": 19.12, "lng": 72.92,
            "phone": "+91-22-5555", "website": "", "address": "Mumbai Suburbs",
            "specialty_score": 0, "osm_id": "h1"
        }
    ]

    # Rank for Cardiology and HIGH risk
    ranked = rank_hospitals(facilities, 19.076, 72.877, "Heart Disease", "HIGH")
    
    assert len(ranked) == 2
    # Cardiology Clinic should rank #1 because of specialty (25%) and closer distance (40%)
    assert ranked[0]["name"] == "Cardiology Clinic"
    assert ranked[0]["rank"] == 1
    
    # Score breakdown assertions
    bd = ranked[0]["score_breakdown"]
    assert bd["specialty"] > 0
    assert bd["distance"] == 100.0  # very close

def test_ai_best_pick_transparent_reasons():
    facilities = [
        {
            "name": "Cardiology Clinic", "type": "clinic", "lat": 19.08, "lng": 72.88,
            "phone": "+91-22-12345", "website": "https://cardiocare.com", "address": "Mumbai",
            "specialty_score": 40, "osm_id": "c1"
        }
    ]
    ranked = rank_hospitals(facilities, 19.076, 72.877, "Heart Disease", "HIGH")
    best = get_ai_best_pick(ranked, "Heart Disease")
    
    assert best is not None
    assert "Specialty Match" in best["ai_explanation"]
    assert "Clinic Facility" in best["ai_explanation"]
    assert "Contact Info" in best["ai_explanation"]
