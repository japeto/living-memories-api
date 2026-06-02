from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.supabase import get_supabase
from main import app


@pytest.fixture
def supabase_mock() -> MagicMock:
    # Fluent query-builder mock: table().select().eq().limit() all chain back to the
    # same object, and execute() is awaitable. Tests override .data per case via
    # `supabase_mock.table.return_value.execute.return_value.data = [...]`.
    client = MagicMock()
    query = client.table.return_value
    query.select.return_value = query
    query.eq.return_value = query
    query.limit.return_value = query
    query.insert.return_value = query
    query.delete.return_value = query
    query.execute = AsyncMock(return_value=MagicMock(data=[]))
    return client


@pytest.fixture
async def client(supabase_mock: MagicMock) -> AsyncIterator[AsyncClient]:
    # The real Supabase client is built in the app lifespan, which httpx's
    # ASGITransport does not run — inject the mock through the dependency instead.
    app.dependency_overrides[get_supabase] = lambda: supabase_mock
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
