from typing import Any

from supabase import AsyncClient


class AuthRepository:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        response = (
            await self._client.table("users")
            .select("id, pin_hash")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    async def create_user(self, email: str, display_name: str, pin_hash: str) -> dict[str, Any]:
        """Insert a new user into the database."""
        response = (
            await self._client.table("users")
            .insert({"email": email, "display_name": display_name, "pin_hash": pin_hash})
            .execute()
        )
        return response.data[0]
