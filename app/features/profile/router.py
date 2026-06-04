from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUserDep
from app.core.supabase import SupabaseDep
from app.features.profile.repository import ProfileRepository
from app.features.profile.schemas import UserProfileResponse
from app.features.profile.service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


def get_profile_service(client: SupabaseDep) -> ProfileService:
    return ProfileService(ProfileRepository(client))


ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]


@router.get("/me")
async def get_me(user_id: CurrentUserDep, service: ProfileServiceDep) -> UserProfileResponse:
    return await service.get_user_profile(user_id)
