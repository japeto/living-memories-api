from fastapi import FastAPI

from app.core.config import settings
from app.core.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the Mi Recuerdo Vivo API"}
