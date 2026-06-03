from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemoryCreateRequest(BaseModel):
    text: str


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    text: str
    topic: str | None = None
    mood: str | None = None
    reminder_text: str | None = None
    created_at: datetime
