from fastapi import APIRouter, Depends, HTTPException
from coach_app.api.deps import get_current_coach
from coach_app.models.schemas import Alert
from shared.database import db
from bson import ObjectId
from typing import List

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

@router.get("/", response_model=List[Alert])
async def get_alerts(coach=Depends(get_current_coach)):
    coach_email = coach["email"]

    # Step 1: Get coach profile
    coach_profile = await db.coach_profile.find_one({"email": coach_email})
    if not coach_profile or "name" not in coach_profile:
        raise HTTPException(status_code=400, detail="Coach profile missing or incomplete")

    coach_name = coach_profile["name"]

    # Step 2: Get all athletes with this coach_name
    athlete_docs = await db.athletes.find({"coach_name": coach_name}).to_list(length=None)
    username_to_name = {a["username"]: a["name"] for a in athlete_docs}
    athlete_usernames = list(username_to_name.keys())

    if not athlete_usernames:
        return []

    # Step 3: Fetch alerts from those athletes
    # cursor = db.alerts.find({"athlete_id": {"$in": athlete_usernames}}).sort("timestamp", -1)
        # ✅ Only show alerts when hydration status actually changed
    cursor = db.alerts.find({
    "athlete_id": {"$in": athlete_usernames},
    "status_change": True
    }).sort("timestamp", -1)

    alerts = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        doc.setdefault("status", "active")
        doc.setdefault("hydration_level", None)
        doc.setdefault("source", None)

        # Attach athlete full name from db.athletes
        athlete_username = doc.get("username")  # pull from alert.username
        doc["athlete_name"] = username_to_name.get(athlete_username, "Unknown")

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
