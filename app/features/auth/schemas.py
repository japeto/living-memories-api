from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    user_id: UUID
    pin: Annotated[str, Field(pattern=r"^\d{4}$")]


class LoginResponse(BaseModel):
    user_id: str
    authenticated: bool


class RegisterRequest(BaseModel):
    display_name: Annotated[str, Field(min_length=2)]
    email: EmailStr
    pin: Annotated[str, Field(pattern=r"^\d{4}$")]
    conditions_accepted: bool

    @field_validator("conditions_accepted")
    @classmethod
    def must_accept_conditions(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debes aceptar las condiciones")
        return v


class RegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
    authenticated: bool
