from unittest.mock import MagicMock

from httpx import AsyncClient


async def test_login_existing_user_returns_authenticated(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = [
        {"id": "user-1", "pin_hash": "hashed-pin"}
    ]

    response = await client.post("/api/v1/auth/login", json={"user_id": "user-1", "pin": "1234"})

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-1", "authenticated": True}


async def test_login_unknown_user_returns_401(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = []

    response = await client.post("/api/v1/auth/login", json={"user_id": "ghost", "pin": "1234"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_non_numeric_pin_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login", json={"user_id": "user-1", "pin": "abcd"})

    assert response.status_code == 422


async def test_login_wrong_length_pin_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login", json={"user_id": "user-1", "pin": "12"})

    assert response.status_code == 422
