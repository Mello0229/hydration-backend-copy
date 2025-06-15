from fastapi import APIRouter, Depends, HTTPException
from coach_app.api.deps import get_current_coach
from coach_app.models.schemas import Alert
from shared.database import db
from bson import ObjectId
from typing import List
from datetime import timezone

router = APIRouter()

# @router.get("/", response_model=List[Alert])
# async def get_alerts(coach=Depends(get_current_coach)):
#     coach_email = coach["email"]

#     # ✅ 1. Get coach profile
#     coach_profile = await db.coach_profile.find_one({"email": coach_email})
#     if not coach_profile or "name" not in coach_profile:
#         raise HTTPException(status_code=400, detail="Coach profile missing or incomplete")
#     coach_name = coach_profile["name"]

#     # ✅ 2. Get athletes under coach
#     athlete_docs = await db.athletes.find({"assigned_by": coach_email}).to_list(length=None)
    
#     # email_to_name = {a["email"]: a["name"] for a in athlete_docs}
#     # athlete_emails = list(email_to_name.keys())

#     username_to_name = {a["name"]: a["name"] for a in athlete_docs}
#     athlete_usernames = list(username_to_name.keys())


#     print("Coach:", coach_email)
#     print("Athlete emails:", athlete_usernames)
#     print("Querying alerts with athlete_id IN:", athlete_usernames)

#     if not athlete_usernames:
#         return []

#     # ✅ 3. Fetch alerts for those athletes
#     cursor = db.alerts.find({
#         "athlete_id": {"$in": athlete_usernames},
#         "status_change": True
#     }).sort("timestamp", -1)

#     alerts = []
#     async for doc in cursor:
#         doc["id"] = str(doc.pop("_id"))

#         if "timestamp" in doc and hasattr(doc["timestamp"], "isoformat"):
#             doc["timestamp"] = doc["timestamp"].replace(tzinfo=timezone.utc).isoformat() + "Z"

#         doc.setdefault("status", "active")
#         doc.setdefault("hydration_level", None)
#         doc.setdefault("source", "unknown")
#         doc.setdefault("coach_message", "")
#         doc.setdefault("hydration_status", "")
#         doc.setdefault("alert_type", "")
#         doc["status_change"] = doc.get("status_change", False)

#         athlete_id = doc.get("athlete_id")
#         doc["athlete_name"] = username_to_name.get(athlete_id, "Unknown")

#         alerts.append(doc)

#     return alerts

@router.get("/", response_model=List[Alert])
async def get_alerts(coach=Depends(get_current_coach)):
    coach_email = coach["email"]

    # ✅ 1. Get coach profile
    coach_profile = await db.coach_profile.find_one({"email": coach_email})
    if not coach_profile or "name" not in coach_profile:
        raise HTTPException(status_code=400, detail="Coach profile missing or incomplete")
    coach_name = coach_profile["name"]

    # ✅ 2. Get athletes under this coach
    athlete_docs = await db.athletes.find({"assigned_by": coach_email}).to_list(length=None)
    athlete_emails = [a["email"] for a in athlete_docs]

    if not athlete_emails:
        return []

    # ✅ 3. Convert emails → usernames (to match alert's athlete_id field)
    user_docs = await db.users.find({"email": {"$in": athlete_emails}}).to_list(length=None)
    email_to_username = {
    u["email"]: u["username"]
    for u in user_docs
    if "email" in u and "username" in u
    }

    username_to_name = {
    u["username"]: u["name"]
    for u in user_docs
    if "username" in u and "name" in u
    }   

    athlete_usernames = list(email_to_username.values())

    print("Coach:", coach_email)
    print("Athlete USERNAMES for alerts:", athlete_usernames)

    # ✅ 4. Query alerts by athlete usernames
    cursor = db.alerts.find({
        "athlete_id": {"$in": athlete_usernames},
        "status_change": True
    }).sort("timestamp", -1)

    alerts = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))

        if "timestamp" in doc and hasattr(doc["timestamp"], "isoformat"):
            doc["timestamp"] = doc["timestamp"].replace(tzinfo=timezone.utc).isoformat()

        doc.setdefault("status", "active")
        doc.setdefault("hydration_level", None)
        doc.setdefault("source", "unknown")
        doc.setdefault("coach_message", "")
        doc.setdefault("hydration_status", "")
        doc.setdefault("alert_type", "")
        doc["status_change"] = doc.get("status_change", False)

        athlete_id = doc.get("athlete_id")
        # doc["athlete_name"] = username_to_name.get(athlete_id, "Unknown")
        def username_to_pretty(name: str) -> str:
            return name.replace(".", " ").title() if name else "Unknown"

        doc["athlete_name"] = username_to_name.get(athlete_id, username_to_pretty(athlete_id))

        alerts.append(doc)

    return alerts

# @router.get("/", response_model=List[Alert])
# async def get_alerts(coach=Depends(get_current_coach)):
#     coach_email = coach["email"]

#     # ✅ 1. Get coach profile
#     coach_profile = await db.coach_profile.find_one({"email": coach_email})
#     if not coach_profile or "name" not in coach_profile:
#         raise HTTPException(status_code=400, detail="Coach profile missing or incomplete")
#     coach_name = coach_profile["name"]

#     # ✅ 2. Get athletes under coach
#     athlete_docs = await db.athletes.find({"assigned_by": coach_email}).to_list(length=None)
#     # username_to_name = {a["username"]: a["name"] for a in athlete_docs}
#     # athlete_usernames = list(username_to_name.keys())
    
#     email_to_name = {a["email"]: a["name"] for a in athlete_docs}
#     athlete_emails = list(email_to_name.keys())

#     if not athlete_emails:
#         return []

#     # ✅ 3. Fetch alerts for those athletes (no filter to ensure it returns)
#     cursor = db.alerts.find({
#         "athlete_id": {"$in": athlete_emails},
#         "status_change": True
#         # Optional: `"status_change": True` if you want filtering again later
#     }).sort("timestamp", -1)

#     alerts = []
#     async for doc in cursor:
#         doc["id"] = str(doc.pop("_id"))

#     if "timestamp" in doc and hasattr(doc["timestamp"], "isoformat"):
#         doc["timestamp"] = doc["timestamp"].replace(tzinfo=timezone.utc).isoformat() + "Z"

#     doc.setdefault("status", "active")
#     doc.setdefault("hydration_level", None)
#     doc.setdefault("source", "unknown")
#     doc.setdefault("coach_message", "")
#     doc.setdefault("hydration_status", "")
#     doc.setdefault("alert_type", "")

#     if "status_change" not in doc:
#         doc["status_change"] = False

#     athlete_id = doc.get("athlete_id")
#     doc["athlete_name"] = email_to_name.get(athlete_id, "Unknown")

#     alerts.append(doc)  # ✅ Now this always runs

#     return alerts

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
