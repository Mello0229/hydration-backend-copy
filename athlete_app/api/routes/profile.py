# athlete_app/api/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException
from athlete_app.models.schemas import AthleteProfile
from athlete_app.api.deps import get_current_user
from athlete_app.core.config import db

router = APIRouter()

@router.post("/profile")
async def update_profile(profile: AthleteProfile, user=Depends(get_current_user)):
    # If coach is provided, verify existence
    if profile.coach_name:
        exists = await db.coach_profile.find_one({"full_name": profile.coach_name})
        if not exists:
            raise HTTPException(status_code=400, detail="Coach not found")

    await db.users.update_one(
        {"username": user["username"]},
        {"$set": {"profile": profile.dict()}}
    )
    return {"message": "Athlete profile updated"}

@router.get("/profile")
async def get_profile(user=Depends(get_current_user)):
    record = await db.users.find_one({"username": user["username"]})
    return record.get("profile", {})
