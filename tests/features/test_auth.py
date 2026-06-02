from unittest.mock import MagicMock

from httpx import AsyncClient
from postgrest.exceptions import APIError
from pytest_mock import MockerFixture

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


async def test_register_successful_returns_201(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.features.auth.service.get_password_hash", return_value="hashed-pin")
    supabase_mock.table.return_value.execute.return_value.data = [
        {
            "id": VALID_UUID,
            "email": "test@example.com",
            "display_name": "Test User",
        }
    ]

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Test User",
            "email": "test@example.com",
            "pin": "1234",
            "conditions_accepted": True,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "user_id": VALID_UUID,
        "email": "test@example.com",
        "display_name": "Test User",
        "authenticated": True,
    }


async def test_register_missing_fields_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Test User",
        },
    )
    assert response.status_code == 422


async def test_register_invalid_email_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Test User",
            "email": "not-an-email",
            "pin": "1234",
            "conditions_accepted": True,
        },
    )
    assert response.status_code == 422


async def test_register_invalid_pin_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Test User",
            "email": "test@example.com",
            "pin": "123",
            "conditions_accepted": True,
        },
    )
    assert response.status_code == 422


async def test_register_conditions_not_accepted_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Test User",
            "email": "test@example.com",
            "pin": "1234",
            "conditions_accepted": False,
        },
    )
    assert response.status_code == 422


async def test_register_existing_email_returns_409(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    mocker.patch("app.features.auth.service.get_password_hash", return_value="hashed-pin")
    supabase_mock.table.return_value.execute.side_effect = APIError(
        {"message": "duplicate key value violates unique constraint", "code": "23505"}
    )

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Test User",
            "email": "test@example.com",
            "pin": "1234",
            "conditions_accepted": True,
        },
    )

    # Need to reset side_effect to avoid bleeding to other tests if it uses the same mock instance?
    # conftest.py returns a new MagicMock for each run
    # (pytest fixture without scope="session" is function scope)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"
