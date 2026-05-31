from typing import Annotated

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    user_id: Annotated[str, Field(min_length=1)]
    pin: Annotated[str, Field(pattern=r"^\d{4}$")]


class LoginResponse(BaseModel):
    user_id: str
    authenticated: bool
