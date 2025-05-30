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
        "full_name": data.coach_name.strip(),
        "role": "coach"
    })
    existing = await db.athletes.find_one({"name": user["username"]})
    if existing:
        return {"message": "Athlete already linked to a coach"}
    if not coach:
        raise HTTPException(status_code=400, detail="Coach not found")

    # 🔄 Assign athlete to coach
    await db.athletes.insert_one({
        "id": str(uuid.uuid4()),
        "name": user["username"],
        "sport": user.get("profile", {}).get("sport", "Unknown"),
        "hydration": 100,
        "assigned_by": coach["email"],
        "status": "Healthy"
    })

    return {"message": "Coach linked successfully"}