# coach-app/api/deps.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from shared.security import decode_token
from shared.database import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/coach/auth/login")

async def get_current_coach(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ You store sub = email
    coach = await db.coaches.find_one({"email": payload["sub"]})
    if coach is None:
        raise HTTPException(status_code=401, detail="Coach not found")
    
    return coach
