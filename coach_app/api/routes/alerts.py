from fastapi import APIRouter, Depends, HTTPException
from coach_app.api.deps import get_current_coach
from coach_app.models.schemas import Alert
from shared.database import db
from bson import ObjectId

router = APIRouter()

# @router.get("/", response_model=list[Alert])
# async def get_alerts(coach=Depends(get_current_coach)):
#     cursor = db.alerts.find({"athlete_id": {"$exists": True}})
#     alerts = []

#     async for doc in cursor:
#         # Convert _id
#         doc["id"] = str(doc.pop("_id"))

#         # Convert timestamp to datetime if it's not already
#         if "timestamp" in doc and hasattr(doc["timestamp"], "isoformat"):
#             doc["timestamp"] = doc["timestamp"]

#         # Set default values for optional fields if missing
#         doc.setdefault("status", "active")
#         doc.setdefault("hydration_level", None)
#         doc.setdefault("source", None)

#         alerts.append(doc)

#     return alerts

@router.get("/", response_model=list[Alert])
async def get_alerts(coach=Depends(get_current_coach)):
    # 🔍 Fetch coach document with assigned athletes
    coach_doc = await db.coaches.find_one({"email": coach["email"]})
    assigned_usernames = coach_doc.get("assigned_athletes", [])

    if not assigned_usernames:
        return []

    # 🔒 Filter alerts by assigned athlete_ids
    cursor = db.alerts.find({
        "athlete_id": {"$in": assigned_usernames}
    }).sort("timestamp", -1)

    alerts = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        doc.setdefault("status", "active")
        doc.setdefault("hydration_level", None)
        doc.setdefault("source", None)
        alerts.append(doc)

    return alerts

@router.get("/{athlete_id}", response_model=list[Alert])
async def get_alerts_by_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    # 🔍 Return all alerts for a single athlete
    cursor = db.alerts.find({"athlete_id": athlete_id}).sort("timestamp", -1)
    alerts = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        doc.setdefault("status", "active")
        doc.setdefault("hydration_level", None)
        doc.setdefault("source", None)
        alerts.append(doc)
    return alerts

@router.post("/")
async def create_alert(data: Alert, coach=Depends(get_current_coach)):
    await db.alerts.insert_one(data.dict())
    return {"message": "Alert created"}

@router.post("/resolve/{alert_id}")
async def resolve_alert(alert_id: str, coach=Depends(get_current_coach)):
    result = await db.alerts.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": {"status": "resolved"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved"}
