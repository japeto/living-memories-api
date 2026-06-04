from fastapi import APIRouter, Depends

from app.core.auth import CurrentUserDep
from app.features.wellness.schemas import WellnessResponse
from app.features.wellness.service import WellnessService, get_wellness_service

router = APIRouter(prefix="/wellness", tags=["wellness"])


@router.get("/current-week", response_model=WellnessResponse)
async def get_current_week(
    user_id: CurrentUserDep,
    service: WellnessService = Depends(get_wellness_service),
) -> WellnessResponse:
    """
    Get the weekly wellness aggregation (mood and topics) for the current user.
    """
    return await service.get_current_week_wellness(user_id=user_id)
