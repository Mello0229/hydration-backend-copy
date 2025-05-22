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

        await save_prediction(input_data, user, hydration_label, combined)

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
            failed_rows.append({"error": str(e), "raw": row})

    if not valid_batch:
        return {
            "status": "error",
            "message": "All rows failed preprocessing",
            "errors": failed_rows
        }

    input_df = pd.DataFrame([d.dict() for d in valid_batch])
    scaled_input = get_scaler().transform(input_df)
    predictions = get_model().predict(scaled_input)

    results = []
    for row, label in zip(valid_batch, predictions):
        input_data = row.dict()
        hydration_label = HYDRATION_LABELS.get(label, "Unknown")
        combined = input_data["combined_metrics"]

        await save_prediction(input_data, user, hydration_label, combined)

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


@router.get("/alerts")
async def get_athlete_alerts(user=Depends(require_athlete)):
    alerts = db.alerts.find({"athlete_id": user["username"]})
    return [doc async for doc in alerts]


async def save_prediction(input_data: dict, user: dict, label: str, combined: float):
    """
    Saves sensor data and prediction to the database.
    Used by both single and batch ingestion.
    """
    await db.sensor_data.insert_one({
        "user": user["username"],
        **input_data,
        "combined_metrics": combined,
        "timestamp": datetime.utcnow()
    })
    await db.predictions.insert_one({
        "user": user["username"],
        "hydration_status": label,
        "timestamp": datetime.utcnow()
    })
