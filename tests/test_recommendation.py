import pytest
from utils.recommendation_engine import get_recommendation

def test_heart_recommendation_escalation():
    # Patient: non-smoker, healthy weight, normal inputs -> MODERATE
    patient_moderate = {
        "age": 40, "smoking": "Non-smoker", "weight_kg": 70, "height_cm": 175,
        "family_history": "", "prev_diseases": ""
    }
    inputs_moderate = {"trestbps": 120, "chol": 200, "age": 40, "exang": 0}
    rec_mod = get_recommendation("Heart Disease", 0.35, patient_moderate, inputs_moderate)
    assert rec_mod["risk_level"] == "MODERATE"
    assert rec_mod["emergency"] is False

    # Patient: smoker, high cholesterol, chest pain -> CRITICAL
    patient_critical = {
        "age": 65, "smoking": "Smoker", "weight_kg": 95, "height_cm": 170,
        "family_history": "Father: Heart Disease", "prev_diseases": "Diabetes"
    }
    inputs_critical = {"trestbps": 165, "chol": 310, "age": 65, "exang": 1}
    rec_crit = get_recommendation("Heart Disease", 0.91, patient_critical, inputs_critical)
    assert rec_crit["risk_level"] == "CRITICAL"
    assert rec_crit["emergency"] is True
    assert "Cardiologist" in rec_crit["specialist"]

def test_diabetes_escalation():
    patient_data = {
        "age": 50, "smoking": "Non-smoker", "weight_kg": 85, "height_cm": 160
    }
    # High risk probability -> HIGH
    inputs_high = {"glucose": 150, "bmi": 33.2, "age": 50, "dpf": 0.65}
    rec_high = get_recommendation("Diabetes", 0.75, patient_data, inputs_high)
    assert rec_high["risk_level"] == "HIGH"
    assert any("HbA1c" in t for t in rec_high["tests"])
    assert "Endocrinologist" in rec_high["specialist"]
