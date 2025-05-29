# coach-app/models/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Athlete(BaseModel):
    id: str
    name: str
    sport: str
    hydration_level: int
    heart_rate: float
    body_temp: float
    sweat_rate: float
    status: str

class Alert(BaseModel):
    id: str
    athlete_id: str
    alert_type: str
    description: str
    timestamp: datetime
    status: Optional[str] = "active"  # ✅ new field

class CoachProfile(BaseModel):
    full_name: str
    sport: str
    email: str
    contact: str

class CoachUser(BaseModel):
    username: str
    password: str