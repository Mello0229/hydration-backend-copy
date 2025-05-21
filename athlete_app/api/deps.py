from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from athlete_app.core.security import decode_token
from athlete_app.core.config import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ Only query by email (token `sub` is email)
    user = await db.users.find_one({"email": payload["sub"]})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # ✅ Role check
    if user.get("role") != "athlete":
        raise HTTPException(status_code=403, detail="Access denied: Not athlete")

    return user

def require_athlete(user=Depends(get_current_user)):
    if user["role"] != "athlete":
        raise HTTPException(status_code=403, detail="Forbidden: Not athlete role")
    return user
