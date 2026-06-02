from typing import Annotated

from fastapi import Depends, Request

from app.core.config import settings
from supabase import AsyncClient, AsyncClientOptions, acreate_client


async def init_supabase() -> AsyncClient:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set to initialize the Supabase client"
        )
    return await acreate_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=AsyncClientOptions(
            postgrest_client_timeout=settings.SUPABASE_TIMEOUT,
            storage_client_timeout=settings.SUPABASE_TIMEOUT,
            schema="public",
        ),
    )


async def close_supabase(client: AsyncClient) -> None:
    # supabase-py 2.30.x exposes no unified aclose(); only Realtime holds long-lived
    # connections, so drop any open channels before releasing the client reference.
    if client.get_channels():
        await client.remove_all_channels()


def get_supabase(request: Request) -> AsyncClient:
    # The client is created once in the app lifespan and reused to keep the
    # underlying httpx connection pool warm across requests.
    return request.app.state.supabase


SupabaseDep = Annotated[AsyncClient, Depends(get_supabase)]
