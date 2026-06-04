import pytest

from app.features.ai_analysis.gemini_service import GeminiService


@pytest.mark.asyncio
async def test_evaluate_memory_parses_json_with_reminders(mocker) -> None:
    # Arrange
    mocker.patch("app.features.ai_analysis.gemini_service.settings.GEMINI_API_KEY", "dummy-key")

    mock_client_class = mocker.patch("app.features.ai_analysis.gemini_service.genai.Client")
    mock_client_instance = mock_client_class.return_value

    # Mock the response
    mock_response = mocker.MagicMock()
    mock_response.text = """```json
{
  "topic": "Salud",
  "mood": "Tranquilo",
  "title": "Cita médica",
  "reminders": [
    {
      "title": "Ir al doctor",
      "due_date": "2026-06-15T09:00:00Z",
      "description": "Llevar los estudios"
    }
  ]
}
```"""

    # The SDK is client.aio.models.generate_content
    # By making the deepest method an AsyncMock, we can await it.
    mock_client_instance.aio.models.generate_content = mocker.AsyncMock(return_value=mock_response)

    service = GeminiService()

    # Act
    result = await service.evaluate_memory("Tengo cita el 15 de junio a las 9 am.")

    # Assert
    assert result.topic == "Salud"
    assert result.mood == "Tranquilo"
    assert result.title == "Cita médica"
    assert len(result.reminders) == 1
    assert result.reminders[0].title == "Ir al doctor"
    assert result.reminders[0].due_date.isoformat() == "2026-06-15T09:00:00+00:00"


@pytest.mark.asyncio
async def test_evaluate_memory_empty_reminders(mocker) -> None:
    # Arrange
    mocker.patch("app.features.ai_analysis.gemini_service.settings.GEMINI_API_KEY", "dummy-key")

    mock_client_class = mocker.patch("app.features.ai_analysis.gemini_service.genai.Client")
    mock_client_instance = mock_client_class.return_value

    mock_response = mocker.MagicMock()
    mock_response.text = """
{
  "topic": "Familia",
  "mood": "Alegre",
  "title": "Visita de los nietos",
  "reminders": []
}
"""

    mock_client_instance.aio.models.generate_content = mocker.AsyncMock(return_value=mock_response)

    service = GeminiService()

    # Act
    result = await service.evaluate_memory("Ayer vinieron mis nietos.")

    # Assert
    assert result.topic == "Familia"
    assert len(result.reminders) == 0


@pytest.mark.asyncio
async def test_evaluate_memory_naive_date_injects_tzinfo(mocker) -> None:
    # Arrange
    mocker.patch("app.features.ai_analysis.gemini_service.settings.GEMINI_API_KEY", "dummy-key")

    mock_client_class = mocker.patch("app.features.ai_analysis.gemini_service.genai.Client")
    mock_client_instance = mock_client_class.return_value

    mock_response = mocker.MagicMock()
    # Notice the due_date lacks 'Z' or offset, meaning it's naive
    mock_response.text = """
{
  "topic": "Salud",
  "mood": "Tranquilo",
  "title": "Cita",
  "reminders": [
    {
      "title": "Naive date test",
      "due_date": "2026-06-15T09:00:00",
      "description": "No timezone offset provided"
    }
  ]
}
"""
    mock_client_instance.aio.models.generate_content = mocker.AsyncMock(return_value=mock_response)
    service = GeminiService()

    # Act
    # We pass a specific timezone
    result = await service.evaluate_memory("Test", time_zone="America/New_York")

    # Assert
    assert len(result.reminders) == 1
    # It should have been given the America/New_York tzinfo
    assert result.reminders[0].due_date.tzinfo is not None
    assert str(result.reminders[0].due_date.tzinfo) == "America/New_York"
