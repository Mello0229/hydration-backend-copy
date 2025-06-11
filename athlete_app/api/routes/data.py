# athlete-app/api/routes/data.py
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from fastapi.responses import JSONResponse
from typing import List
import pandas as pd

from athlete_app.models.schemas import SensorData, RawSensorInput
from athlete_app.api.deps import get_current_user, require_athlete
from athlete_app.core.config import db
from athlete_app.services.predictor import predict_hydration
from athlete_app.services.preprocess import extract_features_from_row, HYDRATION_LABELS
from athlete_app.core.model_loader import get_model, get_scaler
from athlete_app.api.routes.alerts import insert_auto_hydration_alert

router = APIRouter()

@router.post("/receive")
async def receive_data(data: SensorData, user=Depends(require_athlete)):
    input_data = data.dict()

    for key, value in input_data.items():
        if value is None or value <= 0:
            await db.sensor_warnings.insert_one({
                "user": user["username"],
                "missing_field": key,
                "received_data": input_data,
                "timestamp": datetime.utcnow()
            })
            await db.alerts.insert_one({
                "athlete_id": user["username"],
                "alert_type": "SensorWarning",
                "description": f"Missing or invalid value: {key}",
                "timestamp": datetime.utcnow()
            })
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Invalid or missing value for: {key}",
                    "received": input_data
                }
            )

    prediction, combined = predict_hydration(input_data)
    hydration_label = HYDRATION_LABELS.get(prediction, "Unknown")

    await save_prediction(input_data, user, hydration_label, combined)

    if combined < 70:
        alert_type = "CRITICAL"
        title = "Critical Hydration Alert"
        description = f"Dehydrated at {round(combined)}%"
    elif combined < 85:
        alert_type = "WARNING"
        title = "Hydration Dropped"
        description = f"Hydration dropped to {round(combined)}%"
    else:
        alert_type = "REMINDER"
        title = "Hydration OK"
        description = f"Hydrated at {round(combined)}%"

    await db.alerts.insert_one({
        "athlete_id": user["username"],
        "alert_type": alert_type,
        "title": title,
        "description": description,
        "timestamp": datetime.utcnow()
    })

    return {
        "status": "success",
        "hydration_state_prediction": hydration_label,
        "processed_combined_metrics": combined,
        "raw_sensor_data": input_data
    }

# async def save_prediction(input_data: dict, user: dict, label: str, combined: float):
#     timestamp = datetime.utcnow()

#     # Save raw sensor data
#     await db.sensor_data.insert_one({
#         "user": user["username"],
#         **input_data,
#         "combined_metrics": combined,
#         "timestamp": timestamp
#     })

#     # Save prediction result
#     await db.predictions.insert_one({
#         "user": user["username"],
#         "hydration_status": label,
#         "timestamp": timestamp
#     })

#     # Update inline user profile
#     await db.users.update_one(
#         {"username": user["username"]},
#         {"$set": {
#             "profile.latest_prediction": {
#                 "hydration_status": label,
#                 "heart_rate": input_data["heart_rate"],
#                 "body_temperature": input_data["body_temperature"],
#                 "skin_conductance": input_data["skin_conductance"],
#                 "ecg_sigmoid": input_data["ecg_sigmoid"],
#                 "timestamp": timestamp
#             }
#         }}
#     )

#     # ✅ Add this to update db.athletes too
#     await db.athletes.update_one(
#         {"email": user["email"]},
#         {"$set": {
#             "hydration_level": label,
#             "heart_rate": input_data["heart_rate"],
#             "body_temp": input_data["body_temperature"],
#             "skin_conductance": input_data["skin_conductance"],
#             "ecg_sigmoid": input_data["ecg_sigmoid"]
#         }}
#     )

@router.post("/raw-schema")
async def receive_raw_schema(data: RawSensorInput, user=Depends(require_athlete)):
    record = await db.predictions.find_one({"user": user["username"]}, sort=[("timestamp", -1)])
    if record and "_id" in record:
        record["_id"] = str(record["_id"])
    return record or {"hydration_status": "Unknown"}

@router.get("/hydration/status")
async def get_latest_hydration(user=Depends(require_athlete)):
    prediction = await db.predictions.find_one({"user": user["username"]}, sort=[("timestamp", -1)])
    vitals = await db.sensor_data.find_one({"user": user["username"]}, sort=[("timestamp", -1)])

    if not prediction or not vitals:
        raise HTTPException(status_code=404, detail="No hydration data found")

    return {
        "hydration_status": prediction["hydration_status"],
        "heart_rate": vitals["heart_rate"],
        "body_temperature": vitals["body_temperature"],
        "skin_conductance": vitals["skin_conductance"],
        "ecg_sigmoid": vitals["ecg_sigmoid"],
        "timestamp": vitals["timestamp"]
    }


@router.get("/warnings/prediction")
async def get_prediction_warnings(sensor: str = Query(None), user=Depends(require_athlete)):
    cursor = db.predictions.find({"user": user["username"]}).sort("timestamp", -1)
    logs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        logs.append(doc)
    return logs


@router.get("/warnings/sensor")
async def get_sensor_warnings(sensor: str = Query(None), user=Depends(get_current_user)):
    query = {"user": user["username"]}
    if sensor:
        query["missing_field"] = sensor

    cursor = db.sensor_warnings.find(query).sort("timestamp", -1)
    warnings = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        warnings.append(doc)
    return warnings


@router.get("/time")
async def get_server_time():
    return {"timestamp": int(datetime.utcnow().timestamp())}


@router.get("/ping")
async def ping():
    return {"status": "alive"}


# @router.get("/alerts")
# async def get_athlete_alerts(user=Depends(require_athlete)):
#     alerts = db.alerts.find({"athlete_id": user["username"]})
#     return [doc async for doc in alerts]


def map_label_to_percentage(label: str) -> int:
    if label == "Hydrated":
        return 90
    elif label == "Slightly Dehydrated":
        return 75
    elif label == "Dehydrated":
        return 65
    return 0

async def save_prediction(input_data: dict, user: dict, label: str, combined: float):
    hydration_percent = map_label_to_percentage(label)
    timestamp = datetime.utcnow()

    await db.sensor_data.insert_one({
        "user": user["username"],
        **input_data,
        "combined_metrics": combined,
        "timestamp": timestamp
    })

    await db.predictions.insert_one({
        "user": user["username"],
        "hydration_status": label,
        "hydration_percent": hydration_percent,
        "timestamp": timestamp
    })

    await db.users.update_one(
        {"username": user["username"]},
        {"$set": {
            "profile.latest_prediction": {
                "hydration_status": label,
                "hydration_percent": hydration_percent,
                **input_data,
                "timestamp": timestamp
            }
        }}
    )

    await db.athletes.update_one(
        {"email": user["email"]},
        {"$set": {
            "hydration_level": hydration_percent,
            "status": label,
            **input_data
        }}
    )

    await insert_auto_hydration_alert(user, label, hydration_percent)

@router.post("/raw-receive")
async def raw_receive(data: RawSensorInput, user=Depends(require_athlete)):
    """
    Accepts raw sensor input and performs:
    1. Preprocessing (normalization)
    2. Prediction using ML
    3. Save prediction + vitals
    4. Return hydration status
    """
    try:
        # ✅ FIX HERE: Make sure input is a dict, not a list
        input_dict = data.model_dump()  # use `model_dump()` instead of `dict()` (pydantic v2+)
        clean_data = extract_features_from_row(input_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    prediction, combined = predict_hydration(clean_data)
    # hydration_label = HYDRATION_LABELS.get(prediction, "Unknown")
    HYDRATION_LABELS = {
    0: "Hydrated",
    1: "Slightly Dehydrated",
    2: "Dehydrated"
    }
    # hydration_label = HYDRATION_LABELS.get(prediction, "Unknown")
    try:
        hydration_label = HYDRATION_LABELS[prediction] 
    except (IndexError, TypeError): 
        hydration_label = "Unknown"

    await save_prediction(clean_data, user, hydration_label, combined)

    return {
        "status": "success",
        "hydration_state_prediction": hydration_label,
        "processed_combined_metrics": combined,
        "raw_sensor_data": clean_data
    }

# @router.post("/raw-receive")
# async def raw_receive(data: RawSensorInput, user=Depends(require_athlete)):
#     """ 
#     Accepts raw sensor input and performs:
#     1. Preprocessing (normalization)
#     2. Prediction using ML
#     3. Save prediction + vitals
#     4. Return hydration status
#     """
#     try:
#         # Create a buffer variable to filter out unneeded data (e.g., analog_calibration_pin, time, ir)
#         buffer_data = {key: value for key, value in data.dict().items() if key in ['max30105', 'gy906', 'groveGsr', 'ad8232']}
        
#         # Now overwrite the original data with the buffer_data
#         data = RawSensorInput(**buffer_data)  # Convert the filtered dictionary back to RawSensorInput
        
#         # ✅ Step 1: Preprocess raw data
#         clean_data = extract_features_from_row(data.dict())
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     # ✅ Step 2: ML Prediction
#     prediction, combined = predict_hydration(clean_data)
#     hydration_label = HYDRATION_LABELS.get(prediction, "Unknown")

#     # ✅ Step 3: Save to DB
#     await save_prediction(clean_data, user, hydration_label, combined)

#     # ✅ Step 4: Return result
#     return {
#         "status": "success",
#         "hydration_state_prediction": hydration_label,
#         "processed_combined_metrics": combined,
#         "raw_sensor_data": clean_data
#     }