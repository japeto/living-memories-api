import logging

from fastapi import HTTPException, status
from httpx import ConnectError, TimeoutException
from postgrest.exceptions import APIError

from app.features.profile.repository import ProfileRepository
from app.features.profile.schemas import UserProfileResponse

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    async def get_user_profile(self, user_id: str) -> UserProfileResponse:
        try:
            user = await self._repository.get_user_by_id(user_id)
        except (ConnectError, TimeoutException, APIError) as exc:
            logger.error("Supabase error getting user: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserProfileResponse(
            user_id=str(user["id"]),
            email=user["email"],
            display_name=user["display_name"],
            full_name=user.get("full_name"),
            avatar_url=user.get("avatar_url"),
        )
