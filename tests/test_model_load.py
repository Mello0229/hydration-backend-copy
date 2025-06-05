# tests/test_model_load.py

import pytest
import pandas as pd
from athlete_app.core.model_loader import get_model, get_scaler, FEATURE_ORDER

@pytest.fixture
def dummy_input():
    return {
        "heart_rate": 70,
        "body_temperature": 36.5,
        "skin_conductance": 800,
        "ecg_sigmoid": 0.7,
        "combined_metrics": (70 + 36.5 + 800 + 0.7) / 4
    }

def test_model_and_scaler_load():
    model = get_model()
    scaler = get_scaler()
    assert model is not None, "Model failed to load"
    assert scaler is not None, "Scaler failed to load"

def test_prediction_output(dummy_input):
    model = get_model()
    scaler = get_scaler()
    input_df = pd.DataFrame([dummy_input])[FEATURE_ORDER]
    scaled = scaler.transform(input_df)

    prediction = model.predict(scaled)
    assert prediction.shape == (1,), "Prediction output shape mismatch"

    proba = model.predict_proba(scaled)[0].max()
    assert 0 <= proba <= 1, f"Invalid probability score: {proba}"

    print("✅ Prediction:", prediction[0])
    print("📊 Confidence:", round(proba, 4))
