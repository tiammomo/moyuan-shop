from uuid import uuid4
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.store import store
from app.schemas.asset import AssetRead, AssetType, FeaturedImageRead
from app.schemas.common import DataResponse
from app.services.storage import storage_service
from app.services.time import utc_now

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=DataResponse[AssetRead])
async def upload_asset(
    project_id: str = Form(...),
    product_id: str | None = Form(default=None),
    asset_type: AssetType = Form(...),
    file: UploadFile = File(...),
) -> DataResponse[AssetRead]:
    if asset_type not in {"product_source", "reference_image", "brand_asset"}:
        raise HTTPException(status_code=422, detail="asset_type is not uploadable")

    file_info = await storage_service.save_upload(file, asset_type)
    asset_id = f"asset_{uuid4().hex}"
    asset = {
        "id": asset_id,
        "project_id": project_id,
        "product_id": product_id,
        "asset_type": asset_type,
        "storage_key": file_info["storage_key"],
        "url": f"/api/assets/{asset_id}/file",
        "mime_type": file.content_type or "application/octet-stream",
        "width": file_info["width"],
        "height": file_info["height"],
        "file_size": file_info["file_size"],
        "checksum": file_info["checksum"],
        "created_at": utc_now(),
    }
    with store.lock:
        store.assets[asset_id] = asset
    return DataResponse(data=AssetRead(**asset))


@router.get("/featured", response_model=DataResponse[list[FeaturedImageRead]])
def list_featured_images(limit: int = Query(default=12, ge=1, le=50)) -> DataResponse[list[FeaturedImageRead]]:
    items = []
    for image in storage_service.list_featured_images(limit=limit):
        storage_key = image["storage_key"]
        items.append(
            FeaturedImageRead(
                storage_key=storage_key,
                url=f"/api/assets/file?storage_key={quote(storage_key, safe='')}",
                file_size=image["file_size"],
                created_at=image["created_at"],
            )
        )
    return DataResponse(data=items)


@router.get("/file")
def get_storage_file(storage_key: str = Query(...), download: bool = Query(default=False)) -> StreamingResponse:
    return stream_storage_file(storage_key=storage_key, media_type=guess_media_type(storage_key), download=download)


@router.get("/{asset_id}", response_model=DataResponse[AssetRead])
def get_asset(asset_id: str) -> DataResponse[AssetRead]:
    with store.lock:
        asset = store.assets.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return DataResponse(data=AssetRead(**asset))


@router.get("/{asset_id}/file")
def get_asset_file(asset_id: str, download: bool = Query(default=False)) -> StreamingResponse:
    with store.lock:
        asset = store.assets.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return stream_storage_file(storage_key=asset["storage_key"], media_type=asset["mime_type"], download=download)


def stream_storage_file(storage_key: str, media_type: str, download: bool = False) -> StreamingResponse:
    try:
        exists = storage_service.object_exists(storage_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid storage key") from exc
    if not exists:
        raise HTTPException(status_code=404, detail="Asset file not found")

    file_obj, content_length = storage_service.open_file(storage_key)

    def iter_file():
        try:
            while chunk := file_obj.read(1024 * 1024):
                yield chunk
        finally:
            file_obj.close()
            release = getattr(file_obj, "release_conn", None)
            if release:
                release()

    headers = {}
    if content_length is not None:
        headers["Content-Length"] = str(content_length)
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{Path(storage_key).name}"'

    return StreamingResponse(iter_file(), media_type=media_type, headers=headers)


def guess_media_type(storage_key: str) -> str:
    suffix = Path(storage_key).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    if suffix == ".gif":
        return "image/gif"
    return "application/octet-stream"
