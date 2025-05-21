# athlete_app/services/preprocess.py

from typing import Dict
import math

HYDRATION_LABELS = [
    "Hydrated",
    "Slightly Dehydrated",
    "Dehydrated"
]

SENSOR_LIMITS = {
    "bpm": (30, 250),
    "gy906": (30.0, 42.0),
    "groveGsr": (100, 3000),
    "ad8232": (100, 4095),
}

def sigmoid(x: float, k: float = 0.005, center: float = 2040.0) -> float:
    return 1 / (1 + math.exp(-k * (x - center)))

def validate_sensor_value(name: str, value: float) -> bool:
    if name not in SENSOR_LIMITS:
        return True
    min_val, max_val = SENSOR_LIMITS[name]
    return min_val <= value <= max_val

def extract_features_from_row(row: Dict) -> Dict:
    try:
        bpm = float(row.get("max30105", {}).get("bpm", 0))
        temp = float(row.get("gy906", 0))
        gsr = float(row.get("groveGsr", 0))
        ecg = int(row.get("ad8232", 0))

        if not all([
            validate_sensor_value("bpm", bpm),
            validate_sensor_value("gy906", temp),
            validate_sensor_value("groveGsr", gsr),
            validate_sensor_value("ad8232", ecg),
        ]):
            raise ValueError("Sensor reading out of valid range.")

        return {
            "heart_rate": bpm,
            "body_temperature": temp,
            "skin_conductance": gsr,
            "ECG_sigmoid": sigmoid(ecg),
        }
    except Exception as e:
        raise ValueError(f"Invalid sensor data: {e}")
