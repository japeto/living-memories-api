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
            "title": "This is a test memory",
            "transcribed_text": "This is a test memory",
            "tags": ["mock-tag-1", "mock-tag-2"],
            "created_at": "2026-06-03T00:00:00Z",
        }
    ]

    payload = {"transcribed_text": "This is a test memory"}

    response = await client.post(
        "/api/v1/memories/upload",
        headers={"Authorization": "Bearer valid-token"},
        json=payload,
    )

    assert response.status_code == 201
    resp_data = response.json()
    assert resp_data["id"] == "new-memory-id"
    assert resp_data["user_id"] == VALID_UUID
    assert resp_data["title"] == "This is a test memory"
    assert resp_data["transcribed_text"] == "This is a test memory"
    assert resp_data["tags"] == ["mock-tag-1", "mock-tag-2"]


@pytest.mark.asyncio
async def test_upload_memory_unauthorized_returns_401(client: AsyncClient) -> None:
    payload = {"transcribed_text": "This is a test memory"}

    response = await client.post("/api/v1/memories/upload", json=payload)

    assert (
        response.status_code == 403 or response.status_code == 401
    )  # FastAPI HTTPBearer returns 403 if no Authorization header


@pytest.mark.asyncio
async def test_upload_memory_missing_text_returns_422(
    client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    payload = {}  # missing transcribed_text

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

    payload = {"transcribed_text": "This is a test memory"}

    import pytest

    with pytest.raises(RuntimeError, match="Failed to create memory in database"):
        await client.post(
            "/api/v1/memories/upload",
            headers={"Authorization": "Bearer valid-token"},
            json=payload,
        )


@pytest.mark.asyncio
async def test_upload_memory_long_text_truncates_title(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    supabase_mock.table.return_value.execute.return_value.data = [
        {
            "id": "new-memory-id",
            "user_id": VALID_UUID,
            "title": "mocked title",
            "transcribed_text": "x" * 60,
            "tags": ["mock-tag-1", "mock-tag-2"],
            "created_at": "2026-06-03T00:00:00Z",
        }
    ]

    payload = {"transcribed_text": "x" * 60}

    response = await client.post(
        "/api/v1/memories/upload",
        headers={"Authorization": "Bearer valid-token"},
        json=payload,
    )

    assert response.status_code == 201

    # Check that Supabase insert was called with truncated title
    insert_mock = supabase_mock.table.return_value.insert
    insert_mock.assert_called_once()
    inserted_data = insert_mock.call_args[0][0]
    assert inserted_data["title"] == "x" * 50 + "..."
