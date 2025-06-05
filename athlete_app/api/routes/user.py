# athlete-app/api/routes/user.py
from fastapi import APIRouter, HTTPException, Depends
from athlete_app.models.schemas import PasswordChange
from athlete_app.api.deps import get_current_user
from athlete_app.models.schemas import AthleteJoinCoachSchema
from shared.database import db
from shared.security import verify_password
import uuid

router = APIRouter()

@router.post("/password")
async def change_password(data: PasswordChange, user=Depends(get_current_user)):
    if not verify_password(data.current_password, user["password"]):
        raise HTTPException(status_code=403, detail="Incorrect current password")
    await db.users.update_one({"username": user["username"]}, {"$set": {"password": data.new_password}})
    return {"message": "Password changed"}

@router.delete("/delete")
async def delete_account(user=Depends(get_current_user)):
    await db.users.delete_one({"username": user["username"]})
    return {"message": "Account deleted"}

@router.post("/athlete/join")
async def join_coach(data: AthleteJoinCoachSchema, user=Depends(get_current_user)):
    coach = await db["users"].find_one({
        "name": data.coach_name.strip(),
        "role": "coach"
    })

    if not coach:
        raise HTTPException(status_code=400, detail="Coach not found")

    existing = await db.athletes.find_one({"email": user["email"]})
    if existing:
        return {"message": "Athlete already linked to a coach"}

    # Add complete structure as per AthleteDBEntry
    athlete_entry = {
        "id": str(uuid.uuid4()),
        "athlete_id": user.get("profile", {}).get("id", str(uuid.uuid4())),
        "name": user["username"],
        "email": user["email"],
        "sport": user.get("profile", {}).get("sport", "Unknown"),
        "hydration_level": 100,
        "heart_rate": 0,
        "body_temp": 0,
        "skin_conductance": 0,
        "ECG_sigmoid": 0,
        # "sweat_rate": 0,
        "status": "Hydrated",
        "assigned_by": coach["email"]
    }
    await db.athletes.insert_one(athlete_entry)
    return {"message": "Coach linked successfully"}