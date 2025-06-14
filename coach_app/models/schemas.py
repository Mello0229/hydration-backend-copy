# coach-app/models/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorData(BaseModel):
    id: str
    hydration_level: int
    heart_rate: float
    body_temperature: float
    skin_conductance: float
    ecg_sigmoid: float
    combined_metrics: float

class Athlete(BaseModel):
    id: str
    name: str
    sport: str
    hydration_level: int
    heart_rate: float
    body_temperature: float
    skin_conductance: float
    ecg_sigmoid: float
    status: str
    # alerts: list = []

# class Alert(BaseModel):
#     id: str
#     athlete_id: str
#     alert_type: str
#     title: Optional[str] = None
#     description: str
#     timestamp: datetime
#     status: Optional[str] = "active"
#     hydration_level: Optional[float] = None
#     source: Optional[str] = None
#     coach_message: Optional[str] = None

class Alert(BaseModel):
    id: str
    athlete_id: str
    alert_type: str
    title: Optional[str] = None
    description: str
    timestamp: datetime
    status: Optional[str] = "active"
    hydration_level: Optional[float] = None
    source: Optional[str] = None
    athlete_name: Optional[str] = None
    hydration_status: Optional[str] = None
    status_change: Optional[bool] = False
    coach_message: Optional[str] = None

class CoachProfile(BaseModel):
    name: str      
    sport: str
    email: str
    contact: str

class CoachUser(BaseModel):
    username: str
    password: str