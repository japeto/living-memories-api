from unittest.mock import MagicMock

from httpx import AsyncClient, ConnectError
from pytest_mock import MockerFixture

VALID_UUID = "00000000-0000-0000-0000-000000000001"


async def test_get_me_success_returns_200(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = {
        "id": VALID_UUID,
        "email": "test@example.com",
        "display_name": "Test User",
        "full_name": "Test User Full",
        "avatar_url": "https://example.com/avatar.jpg",
    }
    # mock token decode
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    response = await client.get(
        "/api/v1/profile/me", headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == VALID_UUID
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["full_name"] == "Test User Full"
    assert data["avatar_url"] == "https://example.com/avatar.jpg"


async def test_get_me_not_found_returns_404(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = None
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    response = await client.get(
        "/api/v1/profile/me", headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_get_me_db_error_returns_503(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    supabase_mock.table.return_value.execute.side_effect = ConnectError("Connection failed")
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    response = await client.get(
        "/api/v1/profile/me", headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "database unavailable"


async def test_get_me_unauthorized_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/profile/me")
    assert response.status_code == 401
