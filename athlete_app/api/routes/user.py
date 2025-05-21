# athlete-app/api/routes/user.py
from fastapi import APIRouter, HTTPException, Depends
from athlete_app.models.schemas import PasswordChange
from athlete_app.api.deps import get_current_user
from athlete_app.core.config import db
from athlete_app.models.schemas import AthleteJoinCoachSchema
from shared.database import db

router = APIRouter()

@router.post("/password")
async def change_password(data: PasswordChange, user=Depends(get_current_user)):
    if user["password"] != data.current_password:
        raise HTTPException(status_code=403, detail="Incorrect current password")
    await db.users.update_one({"username": user["username"]}, {"$set": {"password": data.new_password}})
    return {"message": "Password changed"}

@router.delete("/delete")
async def delete_account(user=Depends(get_current_user)):
    await db.users.delete_one({"username": user["username"]})
    return {"message": "Account deleted"}

@router.post("/athlete/join")
async def join_coach(data: AthleteJoinCoachSchema):
    coach = await db["users"].find_one({
        "full_name": data.coach_name.strip(),
        "role": "coach"
    })
    if not coach:
        raise HTTPException(status_code=400, detail="Coach not found")
    
    # TODO: optionally link athlete to coach here (e.g., update athlete doc with coach_id)
    return {"message": "Coach validated successfully"}