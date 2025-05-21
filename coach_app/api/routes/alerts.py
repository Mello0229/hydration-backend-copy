from fastapi import APIRouter, Depends
from coach_app.api.deps import get_current_coach  # ✅ auth
from coach_app.models.schemas import Alert
from shared.database import db


router = APIRouter()

router.get("/", response_model=list[Alert])
async def get_all_alerts(coach=Depends(get_current_coach)):
    return [doc async for doc in db.alerts.find()]

@router.get("/{athlete_id}", response_model=list[Alert])
async def get_alerts_by_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    return [doc async for doc in db.alerts.find({"athlete_id": athlete_id})]

@router.post("/")
async def create_alert(data: Alert, coach=Depends(get_current_coach)):
    await db.alerts.insert_one(data.dict())
    return {"message": "Alert created"}