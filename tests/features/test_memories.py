from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.asyncio
async def test_upload_memory_success_returns_201(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    # Mock database insert
    supabase_mock.table.return_value.execute.return_value.data = [
        {
            "id": "new-memory-id",
            "user_id": VALID_UUID,
            "text": "This is a test memory",
            "topic": "General",
            "mood": "Tranquila",
            "reminder_text": None,
            "created_at": "2026-06-03T00:00:00Z",
        }
    ]

    payload = {"text": "This is a test memory"}

    response = await client.post(
        "/api/v1/memories/upload",
        headers={"Authorization": "Bearer valid-token"},
        json=payload,
    )

    assert response.status_code == 201
    resp_data = response.json()
    assert resp_data["id"] == "new-memory-id"
    assert resp_data["user_id"] == VALID_UUID
    assert resp_data["text"] == "This is a test memory"
    assert resp_data["topic"] == "General"
    assert resp_data["mood"] == "Tranquila"


@pytest.mark.asyncio
async def test_upload_memory_unauthorized_returns_401(client: AsyncClient) -> None:
    payload = {"text": "This is a test memory"}

    response = await client.post("/api/v1/memories/upload", json=payload)

    assert (
        response.status_code == 403 or response.status_code == 401
    )  # FastAPI HTTPBearer returns 403 if no Authorization header


@pytest.mark.asyncio
async def test_upload_memory_missing_text_returns_422(
    client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    payload = {}  # missing text

    response = await client.post(
        "/api/v1/memories/upload", headers={"Authorization": "Bearer valid-token"}, json=payload
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upload_memory_db_failure_raises_exception(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    # Simulate empty response data indicating failure
    supabase_mock.table.return_value.execute.return_value.data = []

    payload = {"text": "This is a test memory"}

    import pytest

    with pytest.raises(RuntimeError, match="Failed to create memory in database"):
        await client.post(
            "/api/v1/memories/upload",
            headers={"Authorization": "Bearer valid-token"},
            json=payload,
        )


@pytest.mark.asyncio
async def test_get_memories_success_returns_200(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    supabase_mock.table.return_value.execute.return_value.data = [
        {
            "id": "new-memory-id",
            "user_id": VALID_UUID,
            "text": "This is a test memory",
            "topic": "General",
            "mood": "Tranquila",
            "reminder_text": None,
            "created_at": "2026-06-03T00:00:00Z",
        }
    ]

    response = await client.get(
        "/api/v1/memories",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    resp_data = response.json()
    assert len(resp_data) == 1
    assert resp_data[0]["id"] == "new-memory-id"
    assert resp_data[0]["user_id"] == VALID_UUID
    assert resp_data[0]["text"] == "This is a test memory"


@pytest.mark.asyncio
async def test_get_memories_empty_returns_200(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    supabase_mock.table.return_value.execute.return_value.data = []

    response = await client.get(
        "/api/v1/memories",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    resp_data = response.json()
    assert len(resp_data) == 0


@pytest.mark.asyncio
async def test_get_memories_unauthorized_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/memories")

    assert response.status_code == 403 or response.status_code == 401
