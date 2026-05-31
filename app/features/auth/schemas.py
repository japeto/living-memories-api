from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    user_id: UUID
    pin: Annotated[str, Field(pattern=r"^\d{4}$")]


class LoginResponse(BaseModel):
    user_id: str
    authenticated: bool
