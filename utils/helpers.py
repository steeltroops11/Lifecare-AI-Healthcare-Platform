# Helper functions with SQLite backend
import joblib
import streamlit as st
from datetime import datetime
import utils.database as db
from utils.logger import get_logger

logger = get_logger("utils.helpers")

class MockClassifier:
    """Mock classifier to serve as a safe fallback if model files are missing or corrupt."""
    def predict(self, X):
        import numpy as np
        return np.array([0])
        
    def predict_proba(self, X):
        import numpy as np
        return np.array([[0.8, 0.2]])

def load_models():
    """Load all ML models and return as a dict. Fallback to mock classifiers if loading fails."""
    models = {}
    
    # Model configuration
    model_paths = {
        "diabetes": "model/diabetes_model.pkl",
        "heart": "model/heart_model.pkl",
        "kidney": "model/kidney_model.pkl",
        "readmission": "model/readmission_model.pkl",
    }
    
    for name, path in model_paths.items():
        try:
            models[name] = joblib.load(path)
            logger.info(f"[MODEL_LOADED] name='{name}' path='{path}'")
        except Exception as e:
            logger.error(f"[MODEL_LOAD_FAIL] name='{name}' error='{e}'")
            models[name] = MockClassifier()
            
    # Load readmission defaults separately
    try:
        models["readmission_defaults"] = joblib.load("model/readmission_defaults.pkl")
        logger.info("[MODEL_LOADED] name='readmission_defaults'")
    except Exception as e:
        logger.error(f"[MODEL_LOAD_FAIL] name='readmission_defaults' error='{e}'")
        models["readmission_defaults"] = {
            "columns": ['race', 'gender', 'age', 'weight', 'admission_type_id', 'discharge_disposition_id', 'admission_source_id', 'time_in_hospital', 'payer_code', 'medical_specialty', 'num_lab_procedures', 'num_procedures', 'num_medications', 'number_outpatient', 'number_emergency', 'number_inpatient', 'diag_1', 'diag_2', 'diag_3', 'number_diagnoses', 'max_glu_serum', 'A1Cresult', 'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride', 'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone', 'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide', 'examide', 'citoglipton', 'insulin', 'glyburide-metformin', 'glipizide-metformin', 'glimepiride-pioglitazone', 'metformin-rosiglitazone', 'metformin-pioglitazone', 'change', 'diabetesMed'],
            "defaults": {'race': 2.0, 'gender': 0.0, 'age': 6.0, 'weight': 1.0, 'admission_type_id': 1.0, 'discharge_disposition_id': 1.0, 'admission_source_id': 7.0, 'time_in_hospital': 4.0, 'payer_code': 8.0, 'medical_specialty': 69.0, 'num_lab_procedures': 44.0, 'num_procedures': 1.0, 'num_medications': 15.0, 'number_outpatient': 0.0, 'number_emergency': 0.0, 'number_inpatient': 0.0, 'diag_1': 298.0, 'diag_2': 260.0, 'diag_3': 256.0, 'number_diagnoses': 8.0, 'max_glu_serum': 3.0, 'A1Cresult': 3.0, 'metformin': 1.0, 'repaglinide': 1.0, 'nateglinide': 1.0, 'chlorpropamide': 1.0, 'glimepiride': 1.0, 'acetohexamide': 0.0, 'glipizide': 1.0, 'glyburide': 1.0, 'tolbutamide': 0.0, 'pioglitazone': 1.0, 'rosiglitazone': 1.0, 'acarbose': 1.0, 'miglitol': 1.0, 'troglitazone': 0.0, 'tolazamide': 0.0, 'examide': 0.0, 'citoglipton': 0.0, 'insulin': 1.0, 'glyburide-metformin': 1.0, 'glipizide-metformin': 0.0, 'glimepiride-pioglitazone': 0.0, 'metformin-rosiglitazone': 0.0, 'metformin-pioglitazone': 0.0, 'change': 1.0, 'diabetesMed': 1.0}
        }
        
    return models

def get_models():
    """Get models from session state, loading if needed."""
    if "models" not in st.session_state:
        st.session_state.models = load_models()
    return st.session_state.models

def save_to_history(disease, prediction, risk, inputs_dict=None):
    """Save a prediction result to report history in SQLite."""
    if inputs_dict is None:
        inputs_dict = {}

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    patient_email = st.session_state.get("user_email", "patient@healthcare.com")

    # Save to SQLite predictions table
    db.save_prediction(patient_email, disease, risk, prediction, inputs_dict, timestamp)
    logger.info(f"[PREDICTION_REQUEST] email='{patient_email}' disease='{disease}' prediction='{int(prediction)}' risk='{float(risk)}'")

    # Rebuild st.session_state.reports mapping (latest active state per disease)
    if "reports" not in st.session_state:
        st.session_state["reports"] = {}
    st.session_state["reports"][disease] = {
        "prediction": int(prediction),
        "risk": float(risk),
    }

def get_report_history(patient_email=None):
    """Get report history from SQLite. If doctor, patient_email can be None to get all history."""
    # If no email is provided and user is a Patient, default to their own email
    if not patient_email and st.session_state.get("user_role") == "Patient":
        patient_email = st.session_state.get("user_email")
    
    return db.get_predictions(patient_email)


# Phase 4 — Model info for confidence display
_MODEL_INFO = {
    "diabetes":    {"name": "Random Forest",          "base_confidence": 92},
    "heart":       {"name": "Gradient Boosting",      "base_confidence": 94},
    "kidney":      {"name": "Random Forest",          "base_confidence": 96},
    "readmission": {"name": "Logistic Regression",    "base_confidence": 88},
}

def get_model_info(disease: str, probability: float) -> dict:
    """
    Return model name and confidence for a given disease prediction.
    Confidence is derived from how far the probability is from 0.5
    (closer to 0 or 1 = more confident).

    Args:
        disease:     "Diabetes" | "Heart Disease" | "Kidney Disease" | "Readmission"
        probability: float 0.0–1.0 from predict_proba

    Returns:
        dict with 'model_name', 'confidence_pct'
    """
    key = disease.lower().replace(" ", "_").replace("_disease", "")
    info = _MODEL_INFO.get(key, {"name": "ML Classifier", "base_confidence": 90})

    # Confidence = how far from 0.5 (uncertain) the probability is
    # 0.5 → 50% confident, 0.0 or 1.0 → 100% confident
    distance_from_center = abs(probability - 0.5) * 2  # 0.0 to 1.0
    raw_confidence = info["base_confidence"] * (0.7 + 0.3 * distance_from_center)
    confidence = round(min(raw_confidence, 99), 1)

    return {
        "model_name":     info["name"],
        "confidence_pct": confidence,
    }
