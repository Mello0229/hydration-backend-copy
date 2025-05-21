# athlete-app/models/schemas.py
from pydantic import BaseModel
from typing import Optional, Literal
from pydantic import BaseModel

class SensorData(BaseModel):
    heart_rate: float
    body_temperature: float
    skin_conductance: float
    ecg_sigmoid: float  

class PredictionResult(BaseModel):
    hydration_status: Literal['Hydrated', 'Slightly Dehydrated', 'Dehydrated']

class User(BaseModel):
    username: str
    password: str
    role: Literal['athlete', 'coach']

class UserProfile(BaseModel):
    full_name: Optional[str]
    dob: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    sport: Optional[str]

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class AthleteJoinCoachSchema(BaseModel):
    coach_name: str