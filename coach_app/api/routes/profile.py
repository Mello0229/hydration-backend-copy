# coach_app/api/routes/profile.py

from fastapi import APIRouter, Depends
from coach_app.models.schemas import CoachProfile
from coach_app.api.deps import get_current_coach
from shared.database import db

router = APIRouter()

@router.get("/", response_model=CoachProfile)
async def get_profile(coach=Depends(get_current_coach)):
    print(f"[GET /profile] Authenticated coach: {coach['email']}")
    profile = await db.coach_profile.find_one({"email": coach["email"]})
    return profile or CoachProfile(full_name="", email=coach["email"], contact="", sport="")

@router.put("/")
async def update_profile(data: CoachProfile, coach=Depends(get_current_coach)):
    print(f"[POST /profile] Saving coach profile: {data.dict()}")
    await db.coach_profile.replace_one({"email": coach["email"]}, data.dict(), upsert=True)
    return {"message": "Profile updated"}
