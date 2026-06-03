from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemoryCreateRequest(BaseModel):
    text: str


class GeminiEvaluationResult(BaseModel):
    topic: str
    mood: str
    title: str | None = None
    reminder_text: str | None = None


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    text: str
    topic: str | None = None
    mood: str | None = None
    title: str | None = None
    reminder_text: str | None = None
    status: str
    created_at: datetime
