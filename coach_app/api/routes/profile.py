# coach-app/api/routes/profile.py
from fastapi import APIRouter, Depends
from coach_app.models.schemas import CoachProfile
from coach_app.api.deps import get_current_coach
from shared.database import db

router = APIRouter()

@router.get("/", response_model=CoachProfile)
async def get_profile(coach=Depends(get_current_coach)):
    profile = await db.coach_profile.find_one()
    return profile or CoachProfile(name="", contact_number="", sport_manage="")

@router.put("/")
async def update_profile(data: CoachProfile, coach=Depends(get_current_coach)):
    await db.coach_profile.replace_one({}, data.dict(), upsert=True)
    return {"message": "Profile updated"}

