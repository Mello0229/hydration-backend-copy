# athlete-app/models/schemas.py
from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional, Literal, Dict
from datetime import datetime
from typing import List

class HydrationAlertInput(BaseModel):
    hydration_level: float

class Alert(BaseModel):
    id: str
    alert_type: str
    title: Optional[str]
    description: str
    timestamp: datetime
    status: Optional[str] = "active"
    hydration_level: Optional[float] = None
    source: Optional[str] = "athlete"

class AthleteAlertsResponse(BaseModel):
    alerts: List[Alert]

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
    name: str
    dob: str
    weight: float
    gender: Literal["male", "female", "other"]
    sport: str
    coach_name: Optional[str]

class AthleteDBEntry(BaseModel):
    id: str
    athlete_id: str
    name: str
    email: str
    sport: str
    assigned_by: str
    body_temp: float = 0
    heart_rate: float = 0
    hydration_level: int = 0
    status: str = "Hydrated"
    # sweat_rate: float = 0
    ecg_sigmoid: float = 0
    skin_conductance: float = 0
    
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class AthleteJoinCoachSchema(BaseModel):
    coach_name: str

class RawSensorInput(BaseModel):
    max30105: Dict[str, float]  # e.g., {"bpm": 72}
    gy906: float                # body temp
    groveGsr: float             # skin conductance
    ad8232: int                 # raw ECG value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "max30105": {"bpm": 72},
                "gy906": 36.5,
                "groveGsr": 1200,
                "ad8232": 2048
            }
        }
    )