from unittest.mock import MagicMock

from httpx import AsyncClient

VALID_UUID = "00000000-0000-0000-0000-000000000001"


async def test_login_existing_user_returns_authenticated(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = [
        {"id": VALID_UUID, "pin_hash": "hashed-pin"}
    ]

    response = await client.post("/api/v1/auth/login", json={"user_id": VALID_UUID, "pin": "1234"})

    assert response.status_code == 200
    assert response.json() == {"user_id": VALID_UUID, "authenticated": True}


async def test_login_unknown_user_returns_401(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = []

    response = await client.post("/api/v1/auth/login", json={"user_id": VALID_UUID, "pin": "1234"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_invalid_uuid_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login", json={"user_id": "not-a-uuid", "pin": "1234"}
    )

    assert response.status_code == 422


async def test_login_non_numeric_pin_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login", json={"user_id": VALID_UUID, "pin": "abcd"})

    assert response.status_code == 422


async def test_login_wrong_length_pin_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login", json={"user_id": VALID_UUID, "pin": "12"})

    assert response.status_code == 422
