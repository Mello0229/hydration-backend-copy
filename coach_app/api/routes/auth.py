from fastapi import APIRouter, HTTPException
from shared.schemas import UserLogin, UserSignup
from shared.security import create_access_token, hash_password, verify_password
from athlete_app.core.config import db  # same DB used by coach
from datetime import datetime

router = APIRouter()

@router.post("/signup")
async def signup(data: UserSignup):
    existing = await db.coaches.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = {
        "email": data.email,
        "username": f"{data.first_name.lower()}.{data.last_name.lower()}",
        "password": hash_password(data.password),  # ✅ Secure hash
        "role": data.role,
        "profile": {},
        "settings": {},
        "created_at": datetime.utcnow()
    }

    await db.coaches.insert_one(new_user)
    token = create_access_token({"sub": data.email, "role": data.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
async def login(data: UserLogin):
    user = await db.coaches.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"], "role": "coach"})
    return {"access_token": token, "token_type": "bearer"}


