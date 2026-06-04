from datetime import datetime
from typing import Any

from fastapi import Depends

from app.core.supabase import get_supabase
from supabase import AsyncClient


class WellnessRepository:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_memories_for_date_range(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """
        Retrieves memories for a given user within a date range.
        Returns minimal fields for wellness calculation.
        """
        response = (
            await self.client.table("memories")
            .select("created_at, mood, topic")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .execute()
        )
        return response.data


def get_wellness_repository(client: AsyncClient = Depends(get_supabase)) -> WellnessRepository:
    return WellnessRepository(client)
