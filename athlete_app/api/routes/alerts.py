from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from athlete_app.api.deps import require_athlete
from athlete_app.core.config import db
from fastapi.encoders import jsonable_encoder
from athlete_app.models.schemas import HydrationAlertInput
from bson import ObjectId
from shared.utils import get_status_label, format_status_for_coach

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
            "type": "DEHYDRATED",
            "title": "Critical Hydration Alert",
            "description": (
                "You are in a dehydrated state! Immediate hydration is recommended to prevent fatigue and performance decline."
            )
        }
    elif hydration_level < 85:
        return {
            "type": "SLIGHTLY DEHYDRATED",
            "title": "Hydration Warning",
            "description": (
                "You are slightly dehydrated. Drink 250mL of water to maintain optimal performance."
            )
        }
    else:
        return {
            "type": "HYDRATED",
            "title": "Daily Hydration Goal Reminder",
            "description": (
                "You’ve consumed 1.5L of water today. Keep going!\nYour daily hydration goal is 2.5L."
            )
        }

@router.get("/alerts")
async def get_athlete_alerts(user=Depends(require_athlete)):
    cursor = db.alerts.find({"athlete_id": user["username"]}).sort("timestamp", -1)

    result = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        doc["timestamp"] = doc["timestamp"].isoformat() + "Z"  # ✅ Append 'Z' for UTC
        result.append(doc)

    return result

# @router.post("/alerts/hydration")
# async def insert_hydration_alert(payload: HydrationAlertInput, user=Depends(require_athlete)):
#     hydration_level = payload.hydration_level
#     alert_data = get_hydration_alert_details(hydration_level)
#     coach_msg = get_coach_summary(hydration_level)  # ← Short summary

#     alert = {
#         "athlete_id": user["username"],
#         "alert_type": alert_data["type"],
#         "title": alert_data["title"],
#         "description": alert_data["description"],
#         "hydration_level": hydration_level,
#         "timestamp": datetime.utcnow(),
#         "source": "athlete",
#         "coach_message": coach_msg  # ← This is what the coach will read
#     }

#     result = await db.alerts.insert_one(alert)

#     response = {
#         "status": "inserted",
#         "alert": {
#             "id": str(result.inserted_id),
#             "athlete_id": alert["athlete_id"],
#             "alert_type": alert["alert_type"],
#             "title": alert["title"],
#             "description": alert["description"],
#             "hydration_level": alert["hydration_level"],
#             "timestamp": alert["timestamp"].isoformat(),
#             "source": alert["source"],
#             "coach_message": alert["coach_message"]
#         }
#     }

#     return response

# @router.post("/alerts/hydration")
# async def create_hydration_alert(data: HydrationAlertInput, user=Depends(require_athlete)):
#     hydration_level = data.hydration_level
#     alert_data = get_hydration_alert_details(hydration_level)

#     alert_doc = {
#         "athlete_id": user["username"],               # ✅ Use current user
#         "alert_type": alert_data["type"],
#         "title": alert_data["title"],
#         "description": alert_data["description"],
#         "timestamp": datetime.utcnow(),
#         "status": "active",
#         "hydration_level": hydration_level,
#         "source": "athlete",
#         "coach_message": get_coach_summary(hydration_level)
#     }

#     await db.alerts.insert_one(alert_doc)
#     return {"message": "Hydration alert created"}

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

# athlete_app/api/routes/alerts.py

async def insert_prediction_alert(user: dict, hydration_label: str, hydration_percent: int, source: str = "ml_model"):
    if hydration_percent >= 85:
        return  # skip if hydrated

    athlete_id = user["username"]
    status = get_status_label(hydration_percent)

    # get last hydration status
    latest_preds = await db.predictions.find(
        {"user": user["email"]}
    ).sort("timestamp", -1).to_list(length=2)

    last_status = None
    if len(latest_preds) > 1:
        prev = latest_preds[1]
        last_status = prev.get("hydration_status")

    is_changed = last_status != status

    alert_data = get_hydration_alert_details(hydration_percent)

    # 🔍 Get coach name from athletes collection
    athlete_doc = await db.athletes.find_one({"username": athlete_id})
    coach_name = athlete_doc.get("assigned_by") if athlete_doc else None

    alert_doc = {
        "athlete_id": athlete_id,
        "alert_type": alert_data["type"],
        "title": alert_data["title"],
        "description": alert_data["description"],
        "hydration_level": hydration_percent,
        "hydration_status": status,
        "status_change": is_changed,
        "source": source,
        "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc),
        "status": "active",
        "coach_message": get_coach_summary(hydration_percent) if is_changed else None,
        "coach_name": coach_name  # 🆕 Added coach_name to alert doc
    }

    await db.alerts.insert_one(alert_doc)

# async def insert_auto_hydration_alert(user: dict, hydration_label: str, hydration_percent: int):
#     if hydration_percent >= 85:
#         return  # No alert needed

#     alert_data = get_hydration_alert_details(hydration_percent)

#     alert = {
#         "athlete_id": user["username"],               # ✅ Must be username
#         "alert_type": alert_data["type"],             # ✅ Consistent naming
#         "title": alert_data["title"],
#         "description": alert_data["description"],
#         "hydration_level": hydration_percent,
#         "timestamp": datetime.utcnow(),
#         "source": "ml_model",
#         "coach_message": get_coach_summary(hydration_percent)
#     }

#     await db.alerts.insert_one(alert)

# async def insert_prediction_based_alert(athlete_id: str, hydration_level: float, source: str = "ml_model"):
#     status = get_status_label(hydration_level)

#     # 🔍 Get last hydration status from db.predictions
#     latest_pred = await db.predictions.find(
#         {"athlete_id": athlete_id}
#     ).sort("timestamp", -1).to_list(length=2)

#     last_status = None
#     if len(latest_pred) > 1:
#         prev_level = latest_pred[1].get("hydration_level")
#         if prev_level is not None:
#             last_status = get_status_label(prev_level)

#     is_status_change = status != last_status

#     alert_data = get_hydration_alert_details(hydration_level)

#     alert_doc = {
#         "athlete_id": athlete_id,
#         "alert_type": alert_data["type"],
#         "title": alert_data["title"],
#         "description": alert_data["description"],
#         "coach_message": format_status_for_coach(status) if is_status_change else None,
#         "hydration_status": status,
#         "hydration_level": hydration_level,
#         "timestamp": datetime.utcnow(),
#         "source": source,
#         "status": "active",
#         "status_change": is_status_change
#     }

#     await db.alerts.insert_one(alert_doc)