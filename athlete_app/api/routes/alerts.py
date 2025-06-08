from fastapi import APIRouter, Depends
from datetime import datetime
from athlete_app.api.deps import require_athlete
from athlete_app.core.config import db
from fastapi.encoders import jsonable_encoder
from athlete_app.models.schemas import HydrationAlertInput
from bson import ObjectId

router = APIRouter()

def get_coach_summary(hydration_level: float) -> str:
    if hydration_level < 70:
        return f"Dehydrated at {hydration_level:.0f}%"
    elif hydration_level < 85:
        return f"Hydration dropped to {hydration_level:.0f}%"
    else:
        return f"Hydrated at {hydration_level:.0f}%"


def get_hydration_alert_details(hydration_level: int):
    if hydration_level < 70:
        return {
            "type": "CRITICAL",
            "title": "Critical Hydration Alert",
            "description": (
                "You are in a dehydrated state! Immediate hydration is recommended to prevent fatigue and performance decline."
            )
        }
    elif hydration_level < 85:
        return {
            "type": "WARNING",
            "title": "Hydration Warning",
            "description": (
                "You are slightly dehydrated. Drink 250mL of water to maintain optimal performance."
            )
        }
    else:
        return {
            "type": "REMINDER",
            "title": "Daily Hydration Goal Reminder",
            "description": (
                "You’ve consumed 1.5L of water today. Keep going!\nYour daily hydration goal is 2.5L."
            )
        }

@router.get("/alerts")
async def get_athlete_alerts(user=Depends(require_athlete)):
    alerts = db.alerts.find({"athlete_id": user["username"]})
    return [doc async for doc in alerts]

@router.post("/alerts/hydration")
async def insert_hydration_alert(payload: HydrationAlertInput, user=Depends(require_athlete)):
    hydration_level = payload.hydration_level
    alert_data = get_hydration_alert_details(hydration_level)
    coach_msg = get_coach_summary(hydration_level)  # ← Short summary

    alert = {
        "athlete_id": user["username"],
        "alert_type": alert_data["type"],
        "title": alert_data["title"],
        "description": alert_data["description"],
        "hydration_level": hydration_level,
        "timestamp": datetime.utcnow(),
        "source": "athlete",
        "coach_message": coach_msg  # ← This is what the coach will read
    }

    result = await db.alerts.insert_one(alert)

    response = {
        "status": "inserted",
        "alert": {
            "id": str(result.inserted_id),
            "athlete_id": alert["athlete_id"],
            "alert_type": alert["alert_type"],
            "title": alert["title"],
            "description": alert["description"],
            "hydration_level": alert["hydration_level"],
            "timestamp": alert["timestamp"].isoformat(),
            "source": alert["source"],
            "coach_message": alert["coach_message"]
        }
    }

    return response

async def insert_hydration_alert(payload: HydrationAlertInput, user=Depends(require_athlete)):
    hydration_level = payload.hydration_level
    alert_data = get_hydration_alert_details(hydration_level)
    coach_msg = get_coach_summary(hydration_level)  # ← Short summary

    alert = {
        "athlete_id": user["username"],
        "alert_type": alert_data["type"],
        "title": alert_data["title"],
        "description": alert_data["description"],
        "hydration_level": hydration_level,
        "timestamp": datetime.utcnow(),
        "source": "athlete",
        "coach_message": coach_msg  # ← This is what the coach will read
    }

    result = await db.alerts.insert_one(alert)

    response = {
        "status": "inserted",
        "alert": {
            "id": str(result.inserted_id),
            "athlete_id": alert["athlete_id"],
            "alert_type": alert["alert_type"],
            "title": alert["title"],
            "description": alert["description"],
            "hydration_level": alert["hydration_level"],
            "timestamp": alert["timestamp"].isoformat(),
            "source": alert["source"],
            "coach_message": alert["coach_message"]
        }
    }

    return response

# @router.post("/alerts/hydration")
# async def insert_hydration_alert(payload: HydrationAlertInput, user=Depends(require_athlete)):
#     hydration_level = payload.hydration_level
#     alert_data = get_hydration_alert_details(hydration_level)

#     alert = {
#         "athlete_id": user["username"],
#         "alert_type": alert_data["type"],
#         "title": alert_data["title"],
#         "description": alert_data["description"],
#         "hydration_level": hydration_level,
#         "timestamp": datetime.utcnow(),
#         "source": "athlete"
#     }   

#     await db.alerts.insert_one(alert)
#     return jsonable_encoder({"status": "inserted", "alert": alert})

async def insert_auto_hydration_alert(user: dict, hydration_label: str, hydration_percent: int):
    if hydration_percent >= 85:
        return  # No alert needed

    alert_data = get_hydration_alert_details(hydration_percent)

    alert = {
        "athlete_id": user["username"],
        "type": alert_data["type"],
        "title": alert_data["title"],
        "description": alert_data["description"],
        "prediction_label": hydration_label,
        "hydration_level": hydration_percent,
        "timestamp": datetime.utcnow(),
        "source": "ml_model",  # 💡 clearly mark ML-generated alerts
        "coach_message": get_coach_summary(hydration_percent)  # 💬 short summary for coach
    }

    await db.alerts.insert_one(alert)

# from fastapi import APIRouter, Depends
# from datetime import datetime
# from athlete_app.api.deps import require_athlete
# from athlete_app.core.config import db
# from fastapi.encoders import jsonable_encoder


# router = APIRouter()

# @router.get("/alerts")
# async def get_athlete_alerts(user=Depends(require_athlete)):
#     alerts = db.alerts.find({"athlete_id": user["username"]})
#     return [doc async for doc in alerts]

# @router.post("/alerts/hydration")
# async def insert_hydration_alert(hydration_level: int, user=Depends(require_athlete)):
#     if hydration_level < 70:
#         alert_type = "CRITICAL"
#         title = "Critical Hydration Alert"
#         message = (
#             "You are in a dehydrated state! Immediate hydration is recommended to prevent fatigue and performance decline."
#         )
#     elif hydration_level < 85:
#         alert_type = "WARNING"
#         title = "Hydration Warning"
#         message = (
#             "You are slightly dehydrated. Drink 250mL of water to maintain optimal performance."
#         )
#     else:
#         alert_type = "REMINDER"
#         title = "Daily Hydration Goal Reminder"
#         message = (
#             "You’ve consumed 1.5L of water today. Keep going!\nYour daily hydration goal is 2.5L."
#         )

#     alert = {
#         "athlete_id": user["username"],
#         "type": alert_type,
#         "title": title,
#         "description": message,
#         "timestamp": datetime.utcnow()
#     }

#     await db.alerts.insert_one(alert)
#     return jsonable_encoder({"status": "inserted", "alert": alert})