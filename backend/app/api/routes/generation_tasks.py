from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.store import store
from app.schemas.common import DataResponse
from app.schemas.generation import GenerationResultRead, GenerationTaskCreate, GenerationTaskRead
from app.workers.generation_worker import create_generation_task, run_generation_task

router = APIRouter(prefix="/generation-tasks", tags=["generation-tasks"])


@router.post("", response_model=DataResponse[GenerationTaskRead])
def create_task(
    request: GenerationTaskCreate,
    background_tasks: BackgroundTasks,
) -> DataResponse[GenerationTaskRead]:
    task = create_generation_task(request)
    background_tasks.add_task(run_generation_task, task["id"])
    return DataResponse(data=GenerationTaskRead(**task))


@router.get("/{task_id}", response_model=DataResponse[GenerationTaskRead])
def get_task(task_id: str) -> DataResponse[GenerationTaskRead]:
    with store.lock:
        task = store.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Generation task not found")
    return DataResponse(data=GenerationTaskRead(**task))


@router.get("/{task_id}/results", response_model=DataResponse[list[GenerationResultRead]])
def get_task_results(task_id: str) -> DataResponse[list[GenerationResultRead]]:
    with store.lock:
        if task_id not in store.tasks:
            raise HTTPException(status_code=404, detail="Generation task not found")
        result_ids = store.task_results.get(task_id, [])
        results = [store.results[result_id] for result_id in result_ids if result_id in store.results]
    return DataResponse(data=[GenerationResultRead(**result) for result in results])


@router.post("/{task_id}/cancel", response_model=DataResponse[GenerationTaskRead])
def cancel_task(task_id: str) -> DataResponse[GenerationTaskRead]:
    with store.lock:
        task = store.tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Generation task not found")
        if task["status"] in {"succeeded", "failed", "expired"}:
            raise HTTPException(status_code=409, detail="Task cannot be cancelled")
        task["status"] = "cancelled"
    return DataResponse(data=GenerationTaskRead(**task))
