from fastapi import HTTPException, status

from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import LoginRequest, LoginResponse


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    async def login(self, payload: LoginRequest) -> LoginResponse:
        user = await self._repository.get_user(payload.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        # TODO(US-6): verify payload.pin against user["pin_hash"] with a constant-time
        # password hasher (the hashing dependency is introduced in the US-6 task).
        return LoginResponse(user_id=payload.user_id, authenticated=True)
