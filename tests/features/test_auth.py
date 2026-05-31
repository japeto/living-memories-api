from httpx import AsyncClient


async def test_login_stub_returns_hello_auth(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Auth"}
