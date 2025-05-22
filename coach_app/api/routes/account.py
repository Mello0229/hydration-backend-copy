from fastapi import APIRouter, Depends, HTTPException
from coach_app.api.deps import get_current_coach
from shared.database import db
from shared.security import verify_password, hash_password
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# --------- Models ----------
class CoachPasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class DeleteAccountResponse(BaseModel):
    message: str


# --------- Change Password ----------
@router.post("/password", response_model=DeleteAccountResponse)
async def change_password(data: CoachPasswordChange, coach=Depends(get_current_coach)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if not verify_password(data.current_password, coach["password"]):
        raise HTTPException(status_code=403, detail="Incorrect current password")

    hashed = hash_password(data.new_password)
    await db.coaches.update_one(
        {"email": coach["email"]},
        {"$set": {"password": hashed}}
    )
    return {"message": "Password changed successfully"}


# --------- Delete Account ----------
@router.delete("/delete", response_model=DeleteAccountResponse)
async def delete_account(coach=Depends(get_current_coach)):
    await db.coaches.delete_one({"email": coach["email"]})
    return {"message": "Coach account deleted"}
