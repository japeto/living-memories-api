from fastapi import APIRouter, Depends, status

from app.core.auth import CurrentUserDep
from app.features.memories.schemas import MemoryCreateRequest, MemoryResponse
from app.features.memories.service import MemoriesService, get_memories_service

router = APIRouter(prefix="/memories", tags=["memories"])


@router.post(
    "/upload",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload memory transcribed text",
)
async def upload_memory(
    user_id: CurrentUserDep,
    request: MemoryCreateRequest,
    service: MemoriesService = Depends(get_memories_service),
) -> MemoryResponse:
    """
    Upload transcribed text to create a new memory.
    Returns the created memory structured data.
    """
    return await service.process_and_save_memory(
        user_id=user_id,
        request=request,
    )
