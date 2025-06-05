from fastapi import APIRouter, Depends
from datetime import datetime
from athlete_app.api.deps import require_athlete
from athlete_app.core.config import db
from fastapi.encoders import jsonable_encoder


router = APIRouter()

@router.get("/alerts")
async def get_athlete_alerts(user=Depends(require_athlete)):
    alerts = db.alerts.find({"athlete_id": user["username"]})
    return [doc async for doc in alerts]

@router.post("/alerts/hydration")
async def insert_hydration_alert(hydration_level: int, user=Depends(require_athlete)):
    if hydration_level < 70:
        alert_type = "CRITICAL"
        title = "Critical Hydration Alert"
        message = (
            "You are in a dehydrated state! Immediate hydration is recommended to prevent fatigue and performance decline."
        )
    elif hydration_level < 85:
        alert_type = "WARNING"
        title = "Hydration Warning"
        message = (
            "You are slightly dehydrated. Drink 250mL of water to maintain optimal performance."
        )
    else:
        alert_type = "REMINDER"
        title = "Daily Hydration Goal Reminder"
        message = (
            "You’ve consumed 1.5L of water today. Keep going!\nYour daily hydration goal is 2.5L."
        )

    alert = {
        "athlete_id": user["username"],
        "type": alert_type,
        "title": title,
        "description": message,
        "timestamp": datetime.utcnow()
    }

    await db.alerts.insert_one(alert)
    return jsonable_encoder({"status": "inserted", "alert": alert})