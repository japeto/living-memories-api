from unittest.mock import AsyncMock, MagicMock

import pytest

from app.features.memories.service import MemoriesService


@pytest.mark.asyncio
async def test_evaluate_and_update_memory_creates_reminders_when_present() -> None:
    # Arrange
    mock_repo = MagicMock()
    mock_repo.update_memory = AsyncMock()

    mock_gemini_service = MagicMock()
    mock_gemini_service.evaluate_memory = AsyncMock()

    mock_reminders_service = MagicMock()
    mock_reminders_service.create_reminders = AsyncMock()

    service = MemoriesService(
        repo=mock_repo,
        gemini_service=mock_gemini_service,
        reminders_service=mock_reminders_service,
    )

    # Mock the Gemini result to include reminders
    mock_result = MagicMock()
    mock_result.topic = "General"
    mock_result.mood = "Tranquila"
    mock_result.title = "Test title"
    mock_result.reminders = [MagicMock(title="Test", due_date="2026-10-10", description="Desc")]
    mock_gemini_service.evaluate_memory.return_value = mock_result

    # Act
    await service.evaluate_and_update_memory("mem-123", "Test text")

    # Assert
    mock_gemini_service.evaluate_memory.assert_awaited_once_with("Test text", "UTC")
    mock_repo.update_memory.assert_awaited_once_with(
        "mem-123",
        {
            "topic": "General",
            "mood": "Tranquila",
            "title": "Test title",
            "status": "completed",
        },
    )
    mock_reminders_service.create_reminders.assert_awaited_once_with(
        "mem-123", mock_result.reminders
    )


@pytest.mark.asyncio
async def test_evaluate_and_update_memory_no_reminders() -> None:
    # Arrange
    mock_repo = MagicMock()
    mock_repo.update_memory = AsyncMock()

    mock_gemini_service = MagicMock()
    mock_gemini_service.evaluate_memory = AsyncMock()

    mock_reminders_service = MagicMock()
    mock_reminders_service.create_reminders = AsyncMock()

    service = MemoriesService(
        repo=mock_repo,
        gemini_service=mock_gemini_service,
        reminders_service=mock_reminders_service,
    )

    # Mock the Gemini result with NO reminders
    mock_result = MagicMock()
    mock_result.topic = "General"
    mock_result.mood = "Tranquila"
    mock_result.title = "Test title"
    mock_result.reminders = []
    mock_gemini_service.evaluate_memory.return_value = mock_result

    # Act
    await service.evaluate_and_update_memory("mem-123", "Test text")

    # Assert
    mock_reminders_service.create_reminders.assert_not_awaited()
