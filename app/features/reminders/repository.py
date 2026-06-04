from fastapi import Depends

from app.core.supabase import get_supabase
from supabase._async.client import AsyncClient


class RemindersRepository:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_reminders(self, user_id: str) -> list[dict]:
        response = (
            await self.client.table("reminders")
            .select("*, memories!inner(user_id)")
            .eq("memories.user_id", user_id)
            .execute()
        )

        data = response.data
        # Security Note: Clean the memories key from the data before returning
        for item in data:
            item.pop("memories", None)
        return data

    async def update_reminder(self, reminder_id: str, data: dict, user_id: str) -> dict | None:
        # Tenancy check: Verify reminder belongs to a memory owned by user_id
        check = (
            await self.client.table("reminders")
            .select("id, memories!inner(user_id)")
            .eq("id", reminder_id)
            .eq("memories.user_id", user_id)
            .execute()
        )
        if not check.data:
            return None  # Not found or unauthorized

        update_resp = (
            await self.client.table("reminders").update(data).eq("id", reminder_id).execute()
        )
        if not update_resp.data:
            return None
        return update_resp.data[0]

    async def create_reminders(self, reminders_data: list[dict]) -> list[dict]:
        if not reminders_data:
            return []
        resp = await self.client.table("reminders").insert(reminders_data).execute()
        return resp.data


def get_reminders_repository(
    client: AsyncClient = Depends(get_supabase),
) -> RemindersRepository:
    return RemindersRepository(client)
