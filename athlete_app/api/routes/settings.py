# athlete_app/api/routes/settings.py
from fastapi import APIRouter, Depends
from shared.database import db
from athlete_app.api.deps import get_current_user
from coach_app.models.schemas import UnitsSettings, NotificationSettings

router = APIRouter()

@router.get("/settings/units", response_model=UnitsSettings)
async def get_units(user=Depends(get_current_user)):
    doc = await db.settings.find_one({"user": user["username"], "type": "units"}) or {}
    return UnitsSettings(**doc.get("value", {}))

@router.put("/settings/units")
async def update_units(data: UnitsSettings, user=Depends(get_current_user)):
    await db.settings.update_one(
        {"user": user["username"], "type": "units"},
        {"$set": {"value": data.dict()}},
        upsert=True
    )
    return {"message": "Units updated"}

@router.get("/settings/notifications", response_model=NotificationSettings)
async def get_notifications(user=Depends(get_current_user)):
    doc = await db.settings.find_one({"user": user["username"], "type": "notification"}) or {}
    return NotificationSettings(**doc.get("value", {}))

@router.put("/settings/notifications")
async def update_notifications(data: NotificationSettings, user=Depends(get_current_user)):
    await db.settings.update_one(
        {"user": user["username"], "type": "notification"},
        {"$set": {"value": data.dict()}},
        upsert=True
    )
    return {"message": "Notification settings updated"}
