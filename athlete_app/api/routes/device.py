from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from athlete_app.core.config import db
from athlete_app.api.deps import get_current_user

router = APIRouter()

@router.get("/device/pairing-status")
async def check_pairing_status(user=Depends(get_current_user)):
    one_minute_ago = datetime.utcnow() - timedelta(seconds=60)
    recent = await db.sensor_data.find_one({
        "user": user["username"],
        "timestamp": {"$gte": one_minute_ago}
    })

    return {
        "paired": bool(recent),
        "last_received": recent["timestamp"] if recent else None
    }
@router.get("/device/status")
async def device_status(user=Depends(get_current_user)):
    # For UI compatibility: WiFi, Wristband, Battery
    one_minute_ago = datetime.utcnow() - timedelta(seconds=60)
    recent = await db.sensor_data.find_one({
        "user": user["username"],
        "timestamp": {"$gte": one_minute_ago}
    })

    return {
        "wifi": "Off",  # Placeholder logic
        "wristband": bool(recent),
        "battery": 100  # Placeholder, no battery logic yet
    }
