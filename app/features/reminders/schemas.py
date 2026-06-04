from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    memory_id: str
    title: str
    due_date: datetime
    description: str | None = None
    is_done: bool
    created_at: datetime


class ReminderUpdateRequest(BaseModel):
    is_done: bool
