from typing import Any

from supabase import AsyncClient


class ProfileRepository:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        response = (
            await self._client.table("users")
            .select("id, email, display_name, full_name, avatar_url")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        return response.data
