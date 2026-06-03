from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoryCreateRequest(BaseModel):
    transcribed_text: str


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str | None = None
    transcribed_text: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
