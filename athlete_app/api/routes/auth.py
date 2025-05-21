from fastapi import APIRouter, HTTPException
from shared.schemas import UserLogin
from shared.security import create_access_token
from athlete_app.core.config import db

router = APIRouter()

@router.post("/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email})
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"], "role": "athlete"})
    return {"access_token": token, "token_type": "bearer"}



@router.post("/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email})
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"], "role": "athlete"})
    return {"access_token": token, "token_type": "bearer"}
