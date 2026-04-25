from uuid import uuid4

from app.core.config import get_settings
from app.core.store import store
from app.schemas.generation import GenerationTaskCreate
from app.services.image_provider import ImageGenerationRequest, image_provider
from app.services.prompt_builder import build_prompt
from app.services.storage import storage_service
from app.services.time import utc_now


def create_generation_task(request: GenerationTaskCreate) -> dict:
    settings = get_settings()
    if request.count > settings.max_generation_count:
        raise ValueError(f"count exceeds configured max_generation_count={settings.max_generation_count}")
    now = utc_now()
    task_id = f"task_{uuid4().hex}"
    rendered_prompt = build_prompt(request)
    model_params = {
        "size": request.params.size,
        "quality": request.params.quality,
        "output_format": request.params.output_format,
        "output_compression": request.params.output_compression,
        "provider": settings.image_provider,
    }
    task = {
        "id": task_id,
        "project_id": request.project_id,
        "product_id": request.product_id,
        "created_by": "local-user",
        "status": "queued",
        "image_type": request.image_type,
        "template_id": request.template_id,
        "template_version": 1 if request.template_id else None,
        "input_params": request.params.model_dump(),
        "rendered_prompt": rendered_prompt,
        "model": settings.default_model,
        "model_params": model_params,
        "error_code": None,
        "error_message": None,
        "request_id": None,
        "elapsed_ms": None,
        "started_at": None,
        "finished_at": None,
        "created_at": now,
        "updated_at": now,
    }
    with store.lock:
        store.tasks[task_id] = task
        store.task_results[task_id] = []
    return task


async def run_generation_task(task_id: str) -> None:
    with store.lock:
        task = store.tasks.get(task_id)
        if not task or task["status"] == "cancelled":
            return
        now = utc_now()
        task["status"] = "running"
        task["started_at"] = now
        task["updated_at"] = now

    try:
        response = await image_provider.generate_image(
            ImageGenerationRequest(
                prompt=task["rendered_prompt"],
                size=task["model_params"]["size"],
                quality=task["model_params"]["quality"],
                output_format=task["model_params"]["output_format"],
                output_compression=task["model_params"].get("output_compression"),
            )
        )
        suffix = ".jpg" if response.format == "jpeg" else f".{response.format}"
        file_info = storage_service.save_generated_bytes(response.image_bytes, suffix=suffix)
        asset_id = f"asset_{uuid4().hex}"
        result_id = f"result_{uuid4().hex}"
        created_at = utc_now()
        asset = {
            "id": asset_id,
            "project_id": task["project_id"],
            "product_id": task["product_id"],
            "asset_type": "generated_image",
            "storage_key": file_info["storage_key"],
            "url": f"/api/assets/{asset_id}/file",
            "mime_type": f"image/{response.format}",
            "width": file_info["width"] or response.width,
            "height": file_info["height"] or response.height,
            "file_size": file_info["file_size"],
            "checksum": file_info["checksum"],
            "created_at": created_at,
        }
        thumbnail_id = None
        thumbnail_url = None
        if response.format == "jpeg":
            thumbnail_info = storage_service.save_thumbnail(file_info["path"], suffix=".jpg")
            thumbnail_id = f"asset_{uuid4().hex}"
            thumbnail = {
                "id": thumbnail_id,
                "project_id": task["project_id"],
                "product_id": task["product_id"],
                "asset_type": "thumbnail",
                "storage_key": thumbnail_info["storage_key"],
                "url": f"/api/assets/{thumbnail_id}/file",
                "mime_type": "image/jpeg",
                "width": thumbnail_info["width"],
                "height": thumbnail_info["height"],
                "file_size": thumbnail_info["file_size"],
                "checksum": thumbnail_info["checksum"],
                "created_at": created_at,
            }
            thumbnail_url = thumbnail["url"]
        result = {
            "id": result_id,
            "task_id": task_id,
            "asset_id": asset_id,
            "thumbnail_asset_id": thumbnail_id,
            "url": asset["url"],
            "thumbnail_url": thumbnail_url,
            "width": asset["width"],
            "height": asset["height"],
            "format": response.format,
            "is_favorite": False,
            "score": None,
            "metadata": {"provider": "mock"},
            "created_at": created_at,
        }
        with store.lock:
            store.assets[asset_id] = asset
            if thumbnail_id:
                store.assets[thumbnail_id] = thumbnail
            store.results[result_id] = result
            store.task_results[task_id] = [result_id]
            task = store.tasks[task_id]
            task["status"] = "succeeded"
            task["request_id"] = response.request_id
            task["elapsed_ms"] = response.elapsed_ms
            task["finished_at"] = created_at
            task["updated_at"] = created_at
    except Exception as exc:  # noqa: BLE001 - map internal errors to task state
        now = utc_now()
        with store.lock:
            task = store.tasks[task_id]
            task["status"] = "failed"
            task["error_code"] = "MOCK_PROVIDER_ERROR"
            task["error_message"] = str(exc)
            task["finished_at"] = now
            task["updated_at"] = now
