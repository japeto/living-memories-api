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
        transcribed_text = request.transcribed_text

        # 1. Processing (Mock NLP logic for tags and title)
        # Extract tags and a title from transcribed text
        # For now, use the first 50 characters as the title
        title = transcribed_text[:50] + "..." if len(transcribed_text) > 50 else transcribed_text
        tags = ["mock-tag-1", "mock-tag-2"]

        # 2. Save to Database
        memory_data = {
            "user_id": user_id,
            "title": title,
            "transcribed_text": transcribed_text,
            "tags": tags,
        }

        return await self.repo.create_memory(memory_data)


def get_memories_service(
    repo: MemoriesRepository = Depends(get_memories_repository),
) -> MemoriesService:
    return MemoriesService(repo)
