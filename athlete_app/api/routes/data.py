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
from athlete_app.models.schemas import RawSensorInput, SensorData
from athlete_app.api.deps import require_athlete

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

@router.post("/raw")
async def receive_raw_sensor_data(payload: list[dict], user=Depends(require_athlete)):
    sensor_map = {item['sensor_type']: item for item in payload}
    try:
        heart_rate = float(sensor_map['MAX30102']['value'])
        body_temperature = float(sensor_map['MLX90614']['value'])
        skin_conductance = float(sensor_map['GSR']['value'])
        ecg_raw = int(sensor_map['ECG']['value'])
    except KeyError as e:
        await db.sensor_warnings.insert_one({
            "user": user["username"],
            "missing_field": str(e),
            "received_data": payload,
            "timestamp": datetime.utcnow()
        })
        await db.alerts.insert_one({
            "athlete_id": user["username"],
            "alert_type": "SensorWarning",
            "description": f"Missing sensor: {e}",
            "timestamp": datetime.utcnow()
        })
        return JSONResponse(status_code=400, content={"error": f"Missing sensor: {e}"})

    def sigmoid(ecg_raw, k=0.005, center=2040):
        return 1 / (1 + pow(2.71828, -k * (ecg_raw - center)))

    ecg_sigmoid = sigmoid(ecg_raw)

    structured = {
        "heart_rate": heart_rate,
        "body_temperature": body_temperature,
        "skin_conductance": skin_conductance,
        "ecg_sigmoid": ecg_sigmoid
    }

    structured["combined_metrics"] = (
        heart_rate + body_temperature + skin_conductance + ecg_sigmoid
    ) / 4

    prediction, _ = predict_hydration(structured)
    hydration_label = HYDRATION_LABELS.get(prediction, "Unknown")

    await db.sensor_data.insert_one({
        "user": user["username"],
        **structured,
        "timestamp": datetime.utcnow()
    })

    await db.predictions.insert_one({
        "user": user["username"],
        "hydration_status": hydration_label,
        "timestamp": datetime.utcnow()
    })

    return {
        "prediction": hydration_label,
        "combined_metrics": structured["combined_metrics"]
    }

from athlete_app.models.schemas import SensorData  # already imported

@router.post("/receive-raw-stream")
async def receive_raw_stream(payload: list[dict], user=Depends(require_athlete)):
    valid_batch = []
    failed_rows = []

    for row in payload:
        try:
            features = extract_features_from_row(row)
            valid_batch.append(SensorData(**features))
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

    result = await receive_data(valid_batch, user=user)

    return {
        "status": "partial" if failed_rows else "success",
        "successful_predictions": result,
        "failed_rows": failed_rows,
        "processed_count": len(valid_batch),
        "total_input": len(payload)
    }


@router.post("/raw-schema")
async def receive_raw_schema(data: RawSensorInput, user=Depends(require_athlete)):
    features = extract_features_from_row(data.dict())
    sensor_data = SensorData(**features)
    return await receive_data([sensor_data], user=user)

@router.post("/raw-schema")
async def receive_raw_schema(data: RawSensorInput, user=Depends(require_athlete)):
    record = await db.predictions.find_one(
        {"user": user["username"]}, sort=[("timestamp", -1)]
    )
    if record and "_id" in record:
        record["_id"] = str(record["_id"])
    return record or {"hydration_status": "Unknown"}

@router.get("/warnings")
async def get_warnings(sensor: str = Query(None), user=Depends(require_athlete)):
    cursor = db.predictions.find({"user": user["username"]}).sort("timestamp", -1)
    logs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        logs.append(doc)
    return logs

@router.get("/warnings")
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
