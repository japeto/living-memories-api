from typing import Any

from supabase import AsyncClient


class AuthRepository:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        response = (
            await self._client.table("users")
            .select("id, pin_hash")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None
