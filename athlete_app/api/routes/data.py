# athlete-app/api/routes/data.py
from fastapi import APIRouter, Depends, Request, Query
from datetime import datetime
from fastapi.responses import JSONResponse
from typing import List
from athlete_app.models.schemas import SensorData
from athlete_app.api.deps import get_current_user
from athlete_app.core.config import db
from athlete_app.services.predictor import predict_hydration
from athlete_app.services.preprocess import extract_features_from_row, HYDRATION_LABELS
from athlete_app.models.schemas import RawSensorInput
from athlete_app.api.deps import require_athlete
import pandas as pd
from athlete_app.core.model_loader import get_model, get_scaler


router = APIRouter()

@router.post("/receive")
async def receive_data(data: List[SensorData], user=Depends(require_athlete)):
    results = []

    for entry in data:
        input_data = entry.dict()

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
                return {
                    "status": "error",
                    "message": f"Invalid or missing value for: {key}",
                    "received": input_data
                }

        prediction, combined = predict_hydration(input_data)
        hydration_label = HYDRATION_LABELS.get(prediction, "Unknown")

        await db.sensor_data.insert_one({
            "user": user["username"],
            **input_data,
            "combined_metrics": combined,
            "timestamp": datetime.utcnow()
        })

        await db.predictions.insert_one({
            "user": user["username"],
            "hydration_status": hydration_label,
            "timestamp": datetime.utcnow()
        })

        results.append({
            "raw_sensor_data": input_data,
            "processed_combined_metrics": combined,
            "hydration_state_prediction": hydration_label
        })

    return {
        "status": "success",
        "last_prediction": results[-1] if results else None,
        "all_predictions": results
    }

@router.post("/receive-raw-stream")
async def receive_raw_stream(payload: list[dict], user=Depends(require_athlete)):
    valid_batch = []
    failed_rows = []

    for row in payload:
        try:
            features = extract_features_from_row(row)
            sensor_data = SensorData(**features)
            valid_batch.append(sensor_data)
        except Exception as e:
            failed_rows.append({
                "error": str(e),
                "raw": row
            })

    if not valid_batch:
        return {
            "status": "error",
            "message": "All rows failed preprocessing",
            "errors": failed_rows
        }

    # Prediction
    input_df = pd.DataFrame([d.dict() for d in valid_batch])
    scaled_input = get_scaler().transform(input_df)
    predictions = get_model().predict(scaled_input)

    results = []
    for row, label in zip(valid_batch, predictions):
        input_data = row.dict()
        hydration_label = HYDRATION_LABELS.get(label, "Unknown")
        combined = input_data["combined_metrics"]

        await db.sensor_data.insert_one({
            "user": user["username"],
            **input_data,
            "timestamp": datetime.utcnow()
        })

        await db.predictions.insert_one({
            "user": user["username"],
            "hydration_status": hydration_label,
            "timestamp": datetime.utcnow()
        })

        results.append({
            "raw_sensor_data": input_data,
            "hydration_state_prediction": hydration_label,
            "processed_combined_metrics": combined
        })

    return {
        "status": "partial" if failed_rows else "success",
        "results": results,
        "errors": failed_rows
    }

@router.post("/raw-schema")
async def receive_raw_schema(data: RawSensorInput, user=Depends(require_athlete)):
    record = await db.predictions.find_one(
        {"user": user["username"]}, sort=[("timestamp", -1)]
    )
    if record and "_id" in record:
        record["_id"] = str(record["_id"])
    return record or {"hydration_status": "Unknown"}

@router.get("/latest")
async def get_latest_sensor(user=Depends(require_athlete)):
    sensor = await db.sensor_data.find_one(
        {"user": user["username"]}, sort=[("timestamp", -1)]
    )
    if sensor and "_id" in sensor:
        sensor["_id"] = str(sensor["_id"])
    return sensor or {}

@router.get("/warnings/prediction")
async def get_warnings(sensor: str = Query(None), user=Depends(require_athlete)):
    cursor = db.predictions.find({"user": user["username"]}).sort("timestamp", -1)
    logs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        logs.append(doc)
    return logs

@router.get("/warnings/sensor")
async def get_warnings(sensor: str = Query(None), user=Depends(get_current_user)):
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
