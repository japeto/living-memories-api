from fastapi import APIRouter

from app.features.auth.router import router as auth_router
from app.features.memories.router import router as memories_router
from app.features.reminders.router import router as reminders_router

# Central versioned router — all feature routers are registered here.
# main.py includes only this router; feature routers carry their own prefix and tags.
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(memories_router)
api_router.include_router(reminders_router)
