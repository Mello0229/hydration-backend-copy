# scripts/verify_model.py

import pandas as pd
from athlete_app.core.model_loader import get_model, get_scaler, FEATURE_ORDER

# Dummy input for testing model pipeline
test_input = {
    "heart_rate": 70,
    "body_temperature": 36.5,
    "skin_conductance": 800,  # ensure preprocessing normalization matches
    "ecg_sigmoid": 0.7,
    "combined_metrics": (70 + 36.5 + 800 + 0.7) / 4
}

def verify_model():
    try:
        model = get_model()
        scaler = get_scaler()

        input_df = pd.DataFrame([test_input])[FEATURE_ORDER]
        input_scaled = scaler.transform(input_df)
        prediction = model.predict(input_scaled)[0]
        proba = model.predict_proba(input_scaled)[0].max()

        print("✅ Model and scaler loaded successfully.")
        print("🔮 Prediction:", prediction)
        print("📊 Confidence:", round(proba, 4))
    
    except Exception as e:
        print("❌ Model verification failed:", str(e))

if __name__ == "__main__":
    verify_model()
