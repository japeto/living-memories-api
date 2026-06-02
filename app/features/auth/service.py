import logging
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from httpx import ConnectError, TimeoutException
from postgrest.exceptions import APIError

from app.core.auth import create_access_token, create_refresh_token
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    UserProfileResponse,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    async def _generate_tokens(self, user_id: str) -> tuple[str, str]:
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        try:
            await self._repository.create_refresh_token(
                user_id=user_id, token=refresh_token, expires_at=expires_at
            )
        except (ConnectError, TimeoutException, APIError) as exc:
            logger.error("Supabase err saving refresh token: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc

        return access_token, refresh_token

    async def login(self, payload: LoginRequest) -> LoginResponse:
        try:
            user = await self._repository.get_user_by_email(payload.email)
        except (ConnectError, TimeoutException, APIError) as exc:
            logger.error("Supabase error: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc

        if user is None or not verify_password(payload.pin, user["pin_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        user_id = str(user["id"])
        access_token, refresh_token = await self._generate_tokens(user_id)

        return LoginResponse(
            user_id=user_id,
            display_name=user["display_name"],
            authenticated=True,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        try:
            pin_hash = get_password_hash(payload.pin)
            user = await self._repository.create_user(
                email=payload.email,
                display_name=payload.display_name,
                pin_hash=pin_hash,
            )
        except APIError as exc:
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

        user_id = str(user["id"])
        access_token, refresh_token = await self._generate_tokens(user_id)

        return RegisterResponse(
            user_id=user_id,
            email=user["email"],
            display_name=user["display_name"],
            authenticated=True,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, payload: RefreshTokenRequest) -> LoginResponse:
        try:
            db_token = await self._repository.get_refresh_token(payload.refresh_token)
        except (ConnectError, TimeoutException, APIError) as exc:
            logger.error("Supabase err getting refresh token: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        expires_at = datetime.fromisoformat(db_token["expires_at"])
        if expires_at < datetime.now(UTC):
            # Token expired, delete it
            await self._repository.delete_refresh_token(payload.refresh_token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = str(db_token["user_id"])

        # Revoke old refresh token (Rotation)
        try:
            await self._repository.delete_refresh_token(payload.refresh_token)
        except (ConnectError, TimeoutException, APIError) as exc:
            logger.error("Supabase err deleting refresh token: %s: %s", type(exc).__name__, exc)

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

        access_token, new_refresh_token = await self._generate_tokens(user_id)

        return LoginResponse(
            user_id=user_id,
            display_name=user["display_name"],
            authenticated=True,
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(self, payload: RefreshTokenRequest) -> None:
        try:
            await self._repository.delete_refresh_token(payload.refresh_token)
        except (ConnectError, TimeoutException, APIError) as exc:
            logger.error("Supabase err deleting refresh token: %s: %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from exc

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
        )
