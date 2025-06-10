# athlete-app/models/schemas.py
from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional, Literal, Dict
from datetime import datetime
from enum import Enum
from typing import Optional

class HydrationStatus(str, Enum):
    HYDRATED = "Hydrated"
    SLIGHTLY_DEHYDRATED = "Slightly Dehydrated"
    DEHYDRATED = "Dehydrated"

class AlertType(str, Enum):
    REMINDER = "REMINDER"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class HydrationAlertInput(BaseModel):
    hydration_level: float

class Alert(BaseModel):
    id: str
    athlete_id: Optional[str] = None
    alert_type: AlertType
    title: Optional[str]
    description: str
    timestamp: datetime
    status: Optional[str] = "active"
    hydration_level: Optional[float] = None
    source: Optional[str] = "athlete"
    coach_message: Optional[str] = None

class AthleteAlertsResponse(BaseModel):
    alerts: list[Alert]

class SensorData(BaseModel):
    heart_rate: float
    body_temperature: float
    skin_conductance: float
    ecg_sigmoid: float

class PredictionResult(BaseModel):
    hydration_status: Literal['Hydrated', 'Slightly Dehydrated', 'Dehydrated']
    hydration_level: Optional[float] = None
    timestamp: Optional[datetime] = None

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
    status: HydrationStatus = HydrationStatus.HYDRATED
    # sweat_rate: float = 0
    ecg_sigmoid: float = 0
    skin_conductance: float = 0
    
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class AthleteJoinCoachSchema(BaseModel):
    coach_name: str

class RawSensorInput(BaseModel):
    max30105: Dict[str, float]  # {"bpm": 72, "ir": 25279}
    gy906: float                # body temperature
    groveGsr: float             # skin conductance
    ad8232: int                 # ECG raw value
    analog_calibration_pin: Optional[int] = None
    time: Optional[int] = None  # Unix timestamp

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "max30105": {"bpm": 72, "ir": 25279},
                "gy906": 36.5,
                "groveGsr": 1200,
                "ad8232": 2048,
                "analog_calibration_pin": 760,
                "time": 1749538669
            }
        }
    )