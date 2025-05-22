from fastapi import APIRouter, Depends, HTTPException
from coach_app.api.deps import get_current_coach
from coach_app.models.schemas import Alert
from shared.database import db
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=list[Alert])
async def get_all_alerts(coach=Depends(get_current_coach)):
    return [doc async for doc in db.alerts.find()]

@router.get("/{athlete_id}", response_model=list[Alert])
async def get_alerts_by_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    return [doc async for doc in db.alerts.find({"athlete_id": athlete_id})]

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
