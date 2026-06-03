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


def get_memories_repository(client: AsyncClient = Depends(get_supabase)) -> MemoriesRepository:
    return MemoriesRepository(client)
