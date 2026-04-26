from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from app.core.store import store
from app.schemas.asset import AssetRead, AssetType
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


@router.get("/{asset_id}", response_model=DataResponse[AssetRead])
def get_asset(asset_id: str) -> DataResponse[AssetRead]:
    with store.lock:
        asset = store.assets.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return DataResponse(data=AssetRead(**asset))


@router.get("/{asset_id}/file")
def get_asset_file(asset_id: str, download: bool = Query(default=False)) -> FileResponse:
    with store.lock:
        asset = store.assets.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    try:
        path = storage_service.resolve_storage_key(asset["storage_key"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid storage key") from exc
    if not path.exists():
        raise HTTPException(status_code=404, detail="Asset file not found")
    filename = path.name if download else None
    return FileResponse(path=path, media_type=asset["mime_type"], filename=filename)
