from unittest.mock import MagicMock

from httpx import AsyncClient, ConnectError
from postgrest.exceptions import APIError
from pytest_mock import MockerFixture

VALID_UUID = "00000000-0000-0000-0000-000000000001"
VALID_EMAIL = "test@example.com"


async def test_login_success_returns_200(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = [
        {"id": VALID_UUID, "pin_hash": "hashed-pin", "display_name": "Test User"}
    ]
    mocker.patch("app.features.auth.service.verify_password", return_value=True)

    response = await client.post("/api/v1/auth/login", json={"email": VALID_EMAIL, "pin": "1234"})

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == VALID_UUID
    assert data["display_name"] == "Test User"
    assert data["authenticated"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


async def test_login_unknown_email_returns_401(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = []

    response = await client.post("/api/v1/auth/login", json={"email": VALID_EMAIL, "pin": "1234"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_wrong_pin_returns_401(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = [
        {"id": VALID_UUID, "pin_hash": "hashed-pin", "display_name": "Test User"}
    ]
    mocker.patch("app.features.auth.service.verify_password", return_value=False)

    response = await client.post("/api/v1/auth/login", json={"email": VALID_EMAIL, "pin": "9999"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_invalid_email_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login", json={"email": "not-an-email", "pin": "1234"}
    )
    assert response.status_code == 422


async def test_login_non_numeric_pin_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login", json={"email": VALID_EMAIL, "pin": "abcd"})
    assert response.status_code == 422


async def test_login_wrong_length_pin_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login", json={"email": VALID_EMAIL, "pin": "12"})
    assert response.status_code == 422


async def test_login_db_unavailable_returns_503(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.side_effect = ConnectError("db down")

    response = await client.post("/api/v1/auth/login", json={"email": VALID_EMAIL, "pin": "1234"})

    assert response.status_code == 503
    assert response.json()["detail"] == "database unavailable"


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
    data = response.json()
    assert data["user_id"] == VALID_UUID
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["authenticated"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


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


async def test_refresh_success_returns_200(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = [
        {"user_id": VALID_UUID, "expires_at": "2099-01-01T00:00:00+00:00"}
    ]
    mocker.patch(
        "app.features.auth.repository.AuthRepository.get_user_by_id",
        return_value={"id": VALID_UUID, "email": "test@example.com", "display_name": "Test User"},
    )

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "valid-token"})

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == VALID_UUID
    assert data["display_name"] == "Test User"
    assert data["authenticated"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


async def test_refresh_expired_token_returns_401(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = [
        {"user_id": VALID_UUID, "expires_at": "2000-01-01T00:00:00+00:00"}
    ]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "expired-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"


async def test_refresh_invalid_token_returns_401(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.return_value.data = []

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"


async def test_refresh_db_unavailable_returns_503(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.side_effect = ConnectError("db down")

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "valid-token"})

    assert response.status_code == 503
    assert response.json()["detail"] == "database unavailable"


async def test_logout_success_returns_204(client: AsyncClient, supabase_mock: MagicMock) -> None:
    supabase_mock.table.return_value.execute.return_value.data = []

    response = await client.post("/api/v1/auth/logout", json={"refresh_token": "valid-token"})

    assert response.status_code == 204
    # Supabase execute should be called once for delete
    assert supabase_mock.table.return_value.execute.call_count >= 1


async def test_logout_db_unavailable_returns_503(
    client: AsyncClient, supabase_mock: MagicMock
) -> None:
    supabase_mock.table.return_value.execute.side_effect = ConnectError("db down")

    response = await client.post("/api/v1/auth/logout", json={"refresh_token": "valid-token"})

    assert response.status_code == 503
    assert response.json()["detail"] == "database unavailable"
