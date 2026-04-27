from uuid import uuid4

import httpx

from app.core.config import get_settings
from app.core.store import store
from app.schemas.generation import GenerationTaskCreate
from app.services.image_provider import ImageGenerationRequest, SourceImage, get_image_provider
from app.services.prompt_builder import build_prompt
from app.services.storage import storage_service
from app.services.time import utc_now

MAX_SOURCE_IMAGE_COUNT = 16


def create_generation_task(request: GenerationTaskCreate) -> dict:
    settings = get_settings()
    if request.count > settings.max_generation_count:
        raise ValueError(f"count exceeds configured max_generation_count={settings.max_generation_count}")
    validate_source_assets(request)
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
        "source_asset_ids": request.source_asset_ids,
        "input_params": request.params.model_dump(),
        "rendered_prompt": rendered_prompt,
        "model": settings.default_model,
        "model_params": model_params,
        "count": request.count,
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
        provider = get_image_provider()
        source_images = resolve_source_images(task["source_asset_ids"])
        total_elapsed_ms = 0
        last_response = None
        for index in range(task["count"]):
            response = await provider.generate_image(
                ImageGenerationRequest(
                    prompt=task["rendered_prompt"],
                    model=task["model"],
                    size=task["model_params"]["size"],
                    quality=task["model_params"]["quality"],
                    output_format=task["model_params"]["output_format"],
                    output_compression=task["model_params"].get("output_compression"),
                    source_images=source_images,
                )
            )
            last_response = response
            total_elapsed_ms += response.elapsed_ms
            suffix = ".jpg" if response.format == "jpeg" else f".{response.format}"
            file_info = storage_service.save_generated_bytes(
                response.image_bytes,
                suffix=suffix,
                content_type=f"image/{response.format}",
            )
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
            thumbnail_info = storage_service.save_thumbnail_from_bytes(response.image_bytes, suffix=".jpg")
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
            result = {
                "id": result_id,
                "task_id": task_id,
                "asset_id": asset_id,
                "thumbnail_asset_id": thumbnail_id,
                "url": asset["url"],
                "thumbnail_url": thumbnail["url"],
                "width": asset["width"],
                "height": asset["height"],
                "format": response.format,
                "is_favorite": False,
                "score": None,
                "metadata": {
                    "provider": task["model_params"]["provider"],
                    "variant_key": None,
                    "index": index,
                    "source_asset_ids": task["source_asset_ids"],
                },
                "created_at": created_at,
            }
            with store.lock:
                store.assets[asset_id] = asset
                store.assets[thumbnail_id] = thumbnail
                store.results[result_id] = result
                store.task_results[task_id].append(result_id)

        created_at = utc_now()
        with store.lock:
            task = store.tasks[task_id]
            task["status"] = "succeeded"
            task["request_id"] = last_response.request_id if last_response else None
            task["elapsed_ms"] = total_elapsed_ms
            task["finished_at"] = created_at
            task["updated_at"] = created_at
    except Exception as exc:  # noqa: BLE001 - map internal errors to task state
        now = utc_now()
        with store.lock:
            task = store.tasks[task_id]
            task["status"] = "failed"
            task["error_code"] = map_provider_error_code(exc)
            task["error_message"] = build_failure_message(exc)
            task["finished_at"] = now
            task["updated_at"] = now


def map_provider_error_code(exc: Exception) -> str:
    if isinstance(exc, httpx.TimeoutException):
        return "PROVIDER_TIMEOUT"
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        if status_code in {401, 403}:
            return "PROVIDER_AUTH_FAILED"
        if status_code == 429:
            return "PROVIDER_RATE_LIMITED"
        if status_code == 504:
            return "PROVIDER_TIMEOUT"
        return "PROVIDER_ERROR"
    if "OPENAI_API_KEY" in str(exc):
        return "PROVIDER_AUTH_FAILED"
    return "PROVIDER_ERROR"


def build_failure_message(exc: Exception) -> str:
    if isinstance(exc, httpx.TimeoutException):
        return "模型服务请求超时：后端等待图像生成服务响应超出限制。"
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        detail = extract_response_detail(exc.response)
        if status_code in {401, 403}:
            return f"模型服务鉴权失败（HTTP {status_code}）：{detail or '请检查 OPENAI_API_KEY 或代理服务权限。'}"
        if status_code == 429:
            return f"模型服务限流（HTTP 429）：{detail or '请求过多或额度不足，请稍后再试。'}"
        if status_code == 400:
            return f"模型服务拒绝请求（HTTP 400）：{detail or '请求参数、图片格式或提示词不符合服务要求。'}"
        if status_code == 413:
            return f"上传图片过大（HTTP 413）：{detail or '请压缩商品图或减少参考图数量。'}"
        if status_code == 504:
            return f"模型服务网关超时（HTTP 504）：{detail or '上游生成耗时过长。'}"
        return f"模型服务返回错误（HTTP {status_code}）：{detail or str(exc)}"
    message = str(exc)
    if "OPENAI_API_KEY" in message:
        return "模型服务鉴权失败：后端未配置 OPENAI_API_KEY，或当前 provider 需要该密钥。"
    return message or "生成任务失败：后端未返回具体错误信息。"


def extract_response_detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text.strip()[:800]
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            code = error.get("code")
            if message and code:
                return f"{message}（code: {code}）"
            if message:
                return str(message)
        detail = body.get("detail") or body.get("message")
        if detail:
            return str(detail)
    return str(body)[:800]


def validate_source_assets(request: GenerationTaskCreate) -> None:
    if not request.source_asset_ids:
        return
    if len(request.source_asset_ids) > MAX_SOURCE_IMAGE_COUNT:
        raise ValueError(f"source_asset_ids supports at most {MAX_SOURCE_IMAGE_COUNT} images")
    with store.lock:
        assets = [store.assets.get(asset_id) for asset_id in request.source_asset_ids]
    for asset_id, asset in zip(request.source_asset_ids, assets, strict=False):
        if asset is None:
            raise ValueError(f"source asset not found: {asset_id}")
        if asset["project_id"] != request.project_id:
            raise ValueError(f"source asset does not belong to project: {asset_id}")
        if request.product_id and asset["product_id"] and asset["product_id"] != request.product_id:
            raise ValueError(f"source asset does not belong to product: {asset_id}")
        if asset["asset_type"] not in {"product_source", "reference_image", "brand_asset"}:
            raise ValueError(f"asset is not a valid source image: {asset_id}")


def resolve_source_images(asset_ids: list[str]) -> list[SourceImage]:
    if not asset_ids:
        return []
    with store.lock:
        assets = [store.assets.get(asset_id) for asset_id in asset_ids]

    source_images = []
    for asset_id, asset in zip(asset_ids, assets, strict=False):
        if asset is None:
            raise ValueError(f"source asset not found: {asset_id}")
        if not storage_service.object_exists(asset["storage_key"]):
            raise ValueError(f"source asset file not found: {asset_id}")
        path = storage_service.materialize_storage_key(asset["storage_key"])
        source_images.append(
            SourceImage(
                path=path,
                mime_type=asset["mime_type"],
                filename=path.name,
            )
        )
    return source_images
