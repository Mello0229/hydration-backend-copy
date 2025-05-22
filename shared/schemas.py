# shared/schemas.py
from pydantic import BaseModel, validator
from pydantic.config import ConfigDict
from typing import Literal

class UserSignup(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    role: Literal["athlete", "coach"]

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password": "secure123",
                "confirm_password": "secure123",
                "role": "athlete"
            }
        }
    )

class UserLogin(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "password": "secure123"
            }
        }
    )

def hydration_status_from_percent(level: float) -> str:
    if level >= 85:
        return "Hydrated"
    elif 70 <= level < 85:
        return "Slightly Dehydrated"
    else:
        return "Dehydrated"
