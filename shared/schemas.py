# shared/schemas.py
from pydantic import BaseModel, validator
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

class UserLogin(BaseModel):
    email: str
    password: str