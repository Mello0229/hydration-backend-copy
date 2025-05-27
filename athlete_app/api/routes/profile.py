# athlete_app/api/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException
from athlete_app.models.schemas import UserProfile
from athlete_app.api.deps import get_current_user
from athlete_app.core.config import db

router = APIRouter()

@router.post("/profile")
async def update_profile(profile: UserProfile, user=Depends(get_current_user)):
    print(f"[POST /profile] {user['username']} updating profile as {user['role']}")
    
    if user["role"] == "athlete":
        if not profile.coach_name:
            raise HTTPException(status_code=400, detail="Coach name is required for athletes")
        coach = await db.coach_profile.find_one({"full_name": profile.coach_name})
        if not coach:
            raise HTTPException(status_code=404, detail="Assigned coach does not exist")

    await db.users.update_one(
        {"username": user["username"]},
        {"$set": {"profile": profile.dict()}}
    )
    return {"message": "Profile updated"}
