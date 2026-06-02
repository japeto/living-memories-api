import logging

from fastapi import HTTPException, status
from httpx import ConnectError, TimeoutException
from postgrest.exceptions import APIError

from app.core.security import get_password_hash
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    async def login(self, payload: LoginRequest) -> LoginResponse:
        try:
            user = await self._repository.get_user(payload.user_id)
        except (ConnectError, TimeoutException, APIError) as exc:
            logger.error("Supabase error: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        # TODO(US-6): verify payload.pin against user["pin_hash"] with a constant-time
        # password hasher (the hashing dependency is introduced in the US-6 task).
        return LoginResponse(user_id=str(payload.user_id), authenticated=True)

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        try:
            pin_hash = get_password_hash(payload.pin)
            user = await self._repository.create_user(
                email=payload.email,
                display_name=payload.display_name,
                pin_hash=pin_hash,
            )
        except APIError as exc:
            # Check for unique constraint violation code
            if exc.code == "23505":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                ) from exc
            logger.error("Supabase error: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc
        except (ConnectError, TimeoutException) as exc:
            logger.error("Supabase error: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc

        return RegisterResponse(
            user_id=str(user["id"]),
            email=user["email"],
            display_name=user["display_name"],
            authenticated=True,
        )
