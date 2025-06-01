# coach-app/models/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Athlete(BaseModel):
    id: str
    name: str
    sport: str
    hydration: int
    heart_rate: float
    body_temp: float
    skin_conductance: float
    ecg_sigmoid: float
    status: str
    alerts: list = []
    

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