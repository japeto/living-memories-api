from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.auth import CurrentUserDep
from app.core.supabase import SupabaseDep
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    UserProfileResponse,
)
from app.features.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(client: SupabaseDep) -> AuthService:
    return AuthService(AuthRepository(client))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/login")
async def login(payload: LoginRequest, service: AuthServiceDep) -> LoginResponse:
    return await service.login(payload)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, service: AuthServiceDep) -> RegisterResponse:
    return await service.register(payload)


@router.post("/refresh")
async def refresh(payload: RefreshTokenRequest, service: AuthServiceDep) -> LoginResponse:
    return await service.refresh(payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshTokenRequest, service: AuthServiceDep) -> None:
    await service.logout(payload)


@router.get("/me")
async def get_me(user_id: CurrentUserDep, service: AuthServiceDep) -> UserProfileResponse:
    return await service.get_user_profile(user_id)
