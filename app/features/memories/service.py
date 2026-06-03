from fastapi import Depends

from app.features.memories.repository import MemoriesRepository, get_memories_repository
from app.features.memories.schemas import MemoryCreateRequest, MemoryResponse


class MemoriesService:
    def __init__(self, repo: MemoriesRepository):
        self.repo = repo

    async def process_and_save_memory(
        self, user_id: str, request: MemoryCreateRequest
    ) -> MemoryResponse:
        """
        Processes the transcribed text and saves the structured memory in the database.
        """
        text = request.text

        # 1. Processing (Mock NLP logic for topic and mood)
        topic = "General"
        mood = "Tranquila"

        # 2. Save to Database
        memory_data = {
            "user_id": user_id,
            "text": text,
            "topic": topic,
            "mood": mood,
        }

        return await self.repo.create_memory(memory_data)

    async def list_memories(self, user_id: str) -> list[MemoryResponse]:
        """
        Returns all memories for the given user.
        """
        return await self.repo.get_memories(user_id)


def get_memories_service(
    repo: MemoriesRepository = Depends(get_memories_repository),
) -> MemoriesService:
    return MemoriesService(repo)
