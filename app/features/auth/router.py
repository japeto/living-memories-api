from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.supabase import SupabaseDep
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import LoginRequest, LoginResponse
from app.features.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(client: SupabaseDep) -> AuthService:
    return AuthService(AuthRepository(client))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/login")
async def login(payload: LoginRequest, service: AuthServiceDep) -> LoginResponse:
    return await service.login(payload)
