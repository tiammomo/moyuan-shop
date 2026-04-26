from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.store import store
from app.schemas.common import DataResponse
from app.schemas.generation import GenerationResultRead, GenerationTaskCreate, GenerationTaskRead, PromptPreviewRead
from app.services.prompt_builder import build_prompt, optimize_user_prompt
from app.workers.generation_worker import create_generation_task, run_generation_task

router = APIRouter(prefix="/generation-tasks", tags=["generation-tasks"])


@router.post("/prompt-preview", response_model=DataResponse[PromptPreviewRead])
def preview_prompt(request: GenerationTaskCreate) -> DataResponse[PromptPreviewRead]:
    warnings = []
    if not request.params.prompt:
        warnings.append("未填写创意描述，将只使用商品信息和默认电商约束生成 Prompt。")
    if request.params.include_text:
        warnings.append("精确文案建议由前端后处理叠加，避免依赖模型生成可读文字。")
    return DataResponse(
        data=PromptPreviewRead(
            optimized_prompt=optimize_user_prompt(request.params.prompt),
            rendered_prompt=build_prompt(request),
            warnings=warnings,
        )
    )


@router.post("", response_model=DataResponse[GenerationTaskRead])
def create_task(
    request: GenerationTaskCreate,
    background_tasks: BackgroundTasks,
) -> DataResponse[GenerationTaskRead]:
    try:
        task = create_generation_task(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
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
