from fastapi import Depends, HTTPException

from app.features.memories.schemas import GeminiReminder
from app.features.reminders.repository import RemindersRepository, get_reminders_repository
from app.features.reminders.schemas import ReminderResponse, ReminderUpdateRequest


class RemindersService:
    def __init__(self, repo: RemindersRepository):
        self.repo = repo

    async def get_reminders(self, user_id: str) -> list[ReminderResponse]:
        data = await self.repo.get_reminders(user_id)
        return [ReminderResponse.model_validate(item) for item in data]

    async def update_reminder(
        self, reminder_id: str, request: ReminderUpdateRequest, user_id: str
    ) -> ReminderResponse:
        data = await self.repo.update_reminder(reminder_id, request.model_dump(), user_id)
        if not data:
            raise HTTPException(status_code=404, detail="Reminder not found or unauthorized")
        return ReminderResponse.model_validate(data)

    async def create_reminders(
        self, memory_id: str, reminders: list[GeminiReminder]
    ) -> list[ReminderResponse]:
        if not reminders:
            return []

        reminders_data = []
        for r in reminders:
            reminders_data.append(
                {
                    "memory_id": memory_id,
                    "title": r.title,
                    "due_date": r.due_date.isoformat(),
                    "description": r.description,
                }
            )

        data = await self.repo.create_reminders(reminders_data)
        return [ReminderResponse.model_validate(item) for item in data]


def get_reminders_service(
    repo: RemindersRepository = Depends(get_reminders_repository),
) -> RemindersService:
    return RemindersService(repo)
