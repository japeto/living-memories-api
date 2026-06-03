from typing import Any

from fastapi import Depends

from app.core.supabase import get_supabase
from app.features.memories.schemas import MemoryResponse
from supabase import AsyncClient


class MemoriesRepository:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def create_memory(self, data: dict[str, Any]) -> MemoryResponse:
        """
        Inserts a new memory record into the Supabase database.
        """
        response = await self.client.table("memories").insert(data).execute()
        if not response.data:
            raise RuntimeError("Failed to create memory in database")
        return MemoryResponse(**response.data[0])

    async def get_memories(self, user_id: str) -> list[MemoryResponse]:
        """
        Retrieves all memories for a user, sorted by newest first.
        """
        response = (
            await self.client.table("memories")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return [MemoryResponse(**item) for item in response.data]

    async def update_memory(self, memory_id: str, data: dict[str, Any]) -> MemoryResponse:
        """
        Updates an existing memory record.
        """
        response = await self.client.table("memories").update(data).eq("id", memory_id).execute()
        if not response.data:
            raise RuntimeError(f"Failed to update memory {memory_id}")
        return MemoryResponse(**response.data[0])


def get_memories_repository(client: AsyncClient = Depends(get_supabase)) -> MemoriesRepository:
    return MemoriesRepository(client)
