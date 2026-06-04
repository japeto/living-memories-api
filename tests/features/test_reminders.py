from datetime import UTC
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.asyncio
async def test_get_reminders_success_returns_200(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    # Mock database select
    supabase_mock.table.return_value.execute.return_value.data = [
        {
            "id": "reminder-1",
            "memory_id": "memory-1",
            "title": "Buy milk",
            "due_date": "2026-06-10T10:00:00Z",
            "description": "Don't forget the milk",
            "is_done": False,
            "created_at": "2026-06-03T00:00:00Z",
            "memories": {"user_id": VALID_UUID},  # Should be popped
        }
    ]

    response = await client.get(
        "/api/v1/reminders",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    resp_data = response.json()
    assert len(resp_data) == 1
    assert resp_data[0]["id"] == "reminder-1"
    assert "memories" not in resp_data[0]


@pytest.mark.asyncio
async def test_get_reminders_unauthorized_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/reminders")

    assert response.status_code == 403 or response.status_code == 401


@pytest.mark.asyncio
async def test_update_reminder_success_returns_200(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    # 1. Mock the tenancy check (first execute)
    # 2. Mock the update (second execute)
    check_response = MagicMock()
    check_response.data = [{"id": "reminder-1", "memories": {"user_id": VALID_UUID}}]

    update_response = MagicMock()
    update_response.data = [
        {
            "id": "reminder-1",
            "memory_id": "memory-1",
            "title": "Buy milk",
            "due_date": "2026-06-10T10:00:00Z",
            "description": "Don't forget the milk",
            "is_done": True,
            "created_at": "2026-06-03T00:00:00Z",
        }
    ]

    supabase_mock.table.return_value.execute.side_effect = [check_response, update_response]

    payload = {"is_done": True}
    response = await client.patch(
        "/api/v1/reminders/reminder-1",
        headers={"Authorization": "Bearer valid-token"},
        json=payload,
    )

    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["id"] == "reminder-1"
    assert resp_data["is_done"] is True


@pytest.mark.asyncio
async def test_update_reminder_not_found_or_unauthorized_returns_404(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    # Mock the tenancy check failing (empty data)
    check_response = MagicMock()
    check_response.data = []

    supabase_mock.table.return_value.execute.side_effect = [check_response]

    payload = {"is_done": True}
    response = await client.patch(
        "/api/v1/reminders/reminder-1",
        headers={"Authorization": "Bearer valid-token"},
        json=payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Reminder not found or unauthorized"


@pytest.mark.asyncio
async def test_create_reminders_service_formats_data_correctly(
    supabase_mock: MagicMock,
) -> None:
    from datetime import datetime

    from app.features.memories.schemas import GeminiReminder
    from app.features.reminders.repository import RemindersRepository
    from app.features.reminders.service import RemindersService

    repo = RemindersRepository(client=supabase_mock)
    service = RemindersService(repo=repo)

    mock_insert_response = MagicMock()
    mock_insert_response.data = [
        {
            "id": "new-reminder-1",
            "memory_id": "memory-1",
            "title": "Call doctor",
            "due_date": "2026-06-15T09:00:00Z",
            "description": "Important",
            "is_done": False,
            "created_at": "2026-06-03T00:00:00Z",
        }
    ]
    supabase_mock.table.return_value.insert.return_value.execute.return_value = mock_insert_response

    reminders = [
        GeminiReminder(
            title="Call doctor",
            due_date=datetime(2026, 6, 15, 9, 0, tzinfo=UTC),
            description="Important",
        )
    ]

    result = await service.create_reminders("memory-1", reminders)

    assert len(result) == 1
    assert result[0].id == "new-reminder-1"

    # Verify the mapping was sent to repo
    supabase_mock.table.return_value.insert.assert_called_once_with(
        [
            {
                "memory_id": "memory-1",
                "title": "Call doctor",
                "due_date": "2026-06-15T09:00:00+00:00",
                "description": "Important",
            }
        ]
    )


@pytest.mark.asyncio
async def test_create_reminders_service_empty() -> None:
    from app.features.reminders.service import RemindersService

    mock_repo = MagicMock()
    service = RemindersService(repo=mock_repo)

    result = await service.create_reminders("memory-1", [])
    assert len(result) == 0
    mock_repo.create_reminders.assert_not_called()
