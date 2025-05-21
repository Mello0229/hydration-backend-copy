import pickle
from pathlib import Path
import sys
import traceback

model_path = Path("athlete_app/model/hydration_model.pkl")
scaler_path = Path("athlete_app/model/hydration_scaler.pkl")

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully.")
    print(f"📦 Type: {type(model)}")
    print(f"🎯 Estimator: {model.__class__.__name__}")
except Exception as e:
    print(f"❌ Failed to load model at {model_path}: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    print("✅ Scaler loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load scaler at {scaler_path}: {e}")
    traceback.print_exc()
    sys.exit(1)
