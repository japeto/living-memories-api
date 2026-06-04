import logging

from fastapi import Depends

from app.features.ai_analysis.gemini_service import GeminiService, get_gemini_service
from app.features.memories.repository import MemoriesRepository, get_memories_repository
from app.features.memories.schemas import MemoryCreateRequest, MemoryResponse
from app.features.reminders.service import RemindersService, get_reminders_service

logger = logging.getLogger(__name__)


class MemoriesService:
    def __init__(
        self,
        repo: MemoriesRepository,
        gemini_service: GeminiService,
        reminders_service: RemindersService,
    ):
        self.repo = repo
        self.gemini_service = gemini_service
        self.reminders_service = reminders_service

    async def create_memory(self, user_id: str, request: MemoryCreateRequest) -> MemoryResponse:
        """
        Saves the memory initially as 'processing'.
        """
        memory_data = {
            "user_id": user_id,
            "text": request.text,
            "status": "processing",
        }
        return await self.repo.create_memory(memory_data)

    async def evaluate_and_update_memory(self, memory_id: str, text: str) -> None:
        """
        Background task to evaluate the memory text with Gemini and update the DB.
        """
        try:
            result = await self.gemini_service.evaluate_memory(text)
            update_data = {
                "topic": result.topic,
                "mood": result.mood,
                "title": result.title,
                "status": "completed",
            }
            await self.repo.update_memory(memory_id, update_data)

            if result.reminders:
                await self.reminders_service.create_reminders(memory_id, result.reminders)
        except Exception as e:
            logger.error(f"Failed to evaluate memory {memory_id}: {e}")
            try:
                await self.repo.update_memory(memory_id, {"status": "failed"})
            except Exception as inner_e:
                logger.error(f"Failed to set memory {memory_id} as failed: {inner_e}")

    async def list_memories(self, user_id: str) -> list[MemoryResponse]:
        """
        Returns all memories for the given user.
        """
        return await self.repo.get_memories(user_id)


def get_memories_service(
    repo: MemoriesRepository = Depends(get_memories_repository),
    gemini_service: GeminiService = Depends(get_gemini_service),
    reminders_service: RemindersService = Depends(get_reminders_service),
) -> MemoriesService:
    return MemoriesService(repo, gemini_service, reminders_service)
