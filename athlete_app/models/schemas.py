# athlete-app/models/schemas.py
from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional, Literal, Dict

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
    full_name: str
    dob: str  # format: mm/dd/yyyy or ISO
    weight: float
    gender: Literal["male", "female", "other"]
    sport: str
    coach_name: Optional[str]
    
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