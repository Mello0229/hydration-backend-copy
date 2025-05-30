# athlete_app/api/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException
from athlete_app.models.schemas import UserProfile
from athlete_app.api.deps import get_current_user
from athlete_app.core.config import db
import uuid  # at top

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

        # ✅ Check if already in db.athletes
        existing_athlete = await db.athletes.find_one({"email": user["email"]})
        if not existing_athlete:
            athlete_entry = {
                "id": str(uuid.uuid4()),
                "full_name": profile.full_name,
                "email": user["email"],
                "assigned_by": coach["email"]
            }
            await db.athletes.insert_one(athlete_entry)

    # Continue updating user profile in db.users
    existing = await db.users.find_one({"username": user["username"]})
    existing_profile = existing.get("profile", {})
    if not existing_profile.get("id"):
        profile_data = profile.dict()
        profile_data["id"] = str(uuid.uuid4())
    else:
        profile_data = profile.dict()
        profile_data["id"] = existing_profile["id"]

    await db.users.update_one(
        {"username": user["username"]},
        {"$set": {"profile": profile_data}}
    )
    return {"message": "Profile updated"}
