from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.auth import CurrentUserDep
from app.features.memories.schemas import MemoryCreateRequest, MemoryResponse
from app.features.memories.service import MemoriesService, get_memories_service

router = APIRouter(prefix="/memories", tags=["memories"])


@router.post(
    "/upload",
    response_model=MemoryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload memory transcribed text",
)
async def upload_memory(
    user_id: CurrentUserDep,
    request: MemoryCreateRequest,
    background_tasks: BackgroundTasks,
    service: MemoriesService = Depends(get_memories_service),
) -> MemoryResponse:
    """
    Upload transcribed text to create a new memory.
    Schedules background evaluation and returns the created memory structured data.
    """
    memory = await service.create_memory(
        user_id=user_id,
        request=request,
    )
    background_tasks.add_task(
        service.evaluate_and_update_memory,
        memory.id,
        request.text,
    )
    return memory


@router.get(
    "",
    response_model=list[MemoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all memories for the user",
)
async def list_memories(
    user_id: CurrentUserDep,
    service: MemoriesService = Depends(get_memories_service),
) -> list[MemoryResponse]:
    """
    Returns a list of all memories belonging to the current user.
    """
    return await service.list_memories(user_id=user_id)
