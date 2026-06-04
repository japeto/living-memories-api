from fastapi import APIRouter, Depends

from app.core.auth import CurrentUserDep
from app.features.reminders.schemas import ReminderResponse, ReminderUpdateRequest
from app.features.reminders.service import RemindersService, get_reminders_service

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("", response_model=list[ReminderResponse])
async def get_reminders(
    user_id: CurrentUserDep,
    service: RemindersService = Depends(get_reminders_service),
):
    return await service.get_reminders(user_id)


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    request: ReminderUpdateRequest,
    user_id: CurrentUserDep,
    service: RemindersService = Depends(get_reminders_service),
):
    return await service.update_reminder(reminder_id, request, user_id)
