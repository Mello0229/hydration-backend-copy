# athlete_app/api/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException
from athlete_app.models.schemas import UserProfile, AthleteDBEntry
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

        coach = await db.coach_profile.find_one({"name": profile.coach_name})

        if not coach:
            raise HTTPException(status_code=404, detail="Assigned coach does not exist")

        # ✅ Check if already exists in athletes
        existing_athlete = await db.athletes.find_one({"email": user["email"]})
        if not existing_athlete:
            athlete_entry = AthleteDBEntry(
                id=str(uuid.uuid4()),
                athlete_id=str(user["_id"]),
                name=profile.name,
                email=user["email"],
                sport=profile.sport,
                assigned_by=coach["email"]
            ).dict()
            await db.athletes.insert_one(athlete_entry)
            await db.coaches.update_one(
                {"email": coach["email"]}, 
                {"$addToSet": {"assigned_athletes": user["username"]}}
                )

    # Update user profile in db.users
    profile_data = profile.dict()
    existing = await db.users.find_one({"username": user["username"]})
    existing_profile = existing.get("profile", {})
    profile_data["id"] = existing_profile.get("id", str(uuid.uuid4()))
    profile_data["coach_name"] = profile.coach_name  # ✅ critical line

    await db.users.update_one(
        {"username": user["username"]},
        {"$set": {"profile": profile_data}}
    )
    return {"message": "Profile updated"}
