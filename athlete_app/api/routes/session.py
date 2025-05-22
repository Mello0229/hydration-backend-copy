# athlete_app/api/routes/session.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from athlete_app.api.deps import get_current_user, require_athlete
from athlete_app.core.config import db
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class SessionMetadata(BaseModel):
    title: str
    activity_type: str
    description: Optional[str] = None

@router.post("/session/start")
async def start_session(user=Depends(get_current_user)):
    now = datetime.utcnow()
    sensor = await db.sensor_data.find_one({"user": user["username"]}, sort=[("timestamp", -1)])
    prediction = await db.predictions.find_one({"user": user["username"]}, sort=[("timestamp", -1)])

    session = {
        "user": user["username"],
        "start_time": now,
        "sensor_start": sensor or {},
        "hydration_start": prediction.get("hydration_status") if prediction else None,
        "active": True
    }
    result = await db.sessions.insert_one(session)
    return {"message": "Session started", "session_id": str(result.inserted_id)}

@router.post("/session/end")
async def end_session(meta: SessionMetadata, user=Depends(get_current_user)):
    session = await db.sessions.find_one({"user": user["username"], "active": True}, sort=[("start_time", -1)])
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")

    now = datetime.utcnow()
    sensor = await db.sensor_data.find_one({"user": user["username"]}, sort=[("timestamp", -1)])
    prediction = await db.predictions.find_one({"user": user["username"]}, sort=[("timestamp", -1)])

    update_fields = {
        "end_time": now,
        "sensor_end": sensor or {},
        "hydration_end": prediction.get("hydration_status") if prediction else None,
        "duration": (now - session["start_time"]).total_seconds(),
        "metadata": meta.dict(),
        "active": False
    }
    await db.sessions.update_one({"_id": session["_id"]}, {"$set": update_fields})
    await db.alerts.insert_one({
        "athlete_id": user["username"],
        "alert_type": "ActivitySummary",
        "description": f"New activity: {meta.title}",
        "timestamp": now
    })
    return {"message": "Session ended and saved"}

@router.get("/session/logs")
async def get_session_logs(user=Depends(get_current_user)):
    sessions = db.sessions.find({"user": user["username"]}, sort=[("start_time", -1)])
    results = []
    async for s in sessions:
        s["_id"] = str(s["_id"])
        results.append(s)
    return results

@router.get("/session/{session_id}")
async def get_session_detail(session_id: str, user=Depends(require_athlete)):
    session = await db.sessions.find_one({"_id": ObjectId(session_id), "user": user["username"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["_id"] = str(session["_id"])
    return session
