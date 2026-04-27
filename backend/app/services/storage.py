from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import gettempdir
from typing import BinaryIO
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = self.settings.storage_dir
        self._minio_client = None

    @property
    def backend(self) -> str:
        return self.settings.storage_backend

    def ensure_directories(self) -> None:
        for name in ["assets", "generated", "thumbnails", "exports", "cache"]:
            (self.root / name).mkdir(parents=True, exist_ok=True)
        if self.backend == "minio":
            self.ensure_bucket()

    async def save_upload(self, file: UploadFile, asset_type: str) -> dict:
        suffix = Path(file.filename or "upload.bin").suffix or ".bin"
        filename = f"{uuid4().hex}{suffix}"
        storage_key = f"assets/{asset_type}/{filename}"
        content = await file.read()
        return self.save_bytes(
            content,
            storage_key=storage_key,
            content_type=file.content_type or "application/octet-stream",
        )

    def save_generated_bytes(self, content: bytes, suffix: str = ".jpg", content_type: str | None = None) -> dict:
        filename = f"{uuid4().hex}{suffix}"
        storage_key = f"generated/{filename}"
        return self.save_bytes(content, storage_key=storage_key, content_type=content_type or guess_content_type(suffix))

    def save_thumbnail_from_bytes(self, content: bytes, suffix: str = ".jpg") -> dict:
        filename = f"{uuid4().hex}{suffix}"
        storage_key = f"thumbnails/{filename}"
        with Image.open(BytesIO(content)) as image:
            image.thumbnail((384, 384))
            output = BytesIO()
            image.convert("RGB").save(output, format="JPEG", quality=82)
        return self.save_bytes(output.getvalue(), storage_key=storage_key, content_type="image/jpeg")

    def save_thumbnail(self, source_path: Path, suffix: str = ".jpg") -> dict:
        return self.save_thumbnail_from_bytes(source_path.read_bytes(), suffix=suffix)

    def save_bytes(self, content: bytes, storage_key: str, content_type: str) -> dict:
        self.ensure_directories()
        if self.backend == "minio":
            self.minio_client.put_object(
                self.settings.minio_bucket,
                storage_key,
                BytesIO(content),
                length=len(content),
                content_type=content_type,
            )
            return self.describe_bytes(content, storage_key)

        path = self.resolve_storage_key(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return self.describe_bytes(content, storage_key, path=path)

    def describe_bytes(self, content: bytes, storage_key: str, path: Path | None = None) -> dict:
        width = None
        height = None
        try:
            with Image.open(BytesIO(content)) as image:
                width, height = image.size
        except UnidentifiedImageError:
            pass
        return {
            "path": path,
            "storage_key": storage_key,
            "file_size": len(content),
            "checksum": sha256(content).hexdigest(),
            "width": width,
            "height": height,
        }

    def resolve_storage_key(self, storage_key: str) -> Path:
        path = (self.root / storage_key).resolve()
        root = self.root.resolve()
        if root not in path.parents and path != root:
            raise ValueError("Invalid storage key")
        return path

    def materialize_storage_key(self, storage_key: str) -> Path:
        if self.backend == "local":
            return self.resolve_storage_key(storage_key)

        path = (Path(gettempdir()) / "moyuan-shop-minio-cache" / storage_key).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.minio_client.fget_object(self.settings.minio_bucket, storage_key, str(path))
        return path

    def object_exists(self, storage_key: str) -> bool:
        if self.backend == "local":
            return self.resolve_storage_key(storage_key).exists()
        try:
            self.minio_client.stat_object(self.settings.minio_bucket, storage_key)
        except Exception:  # noqa: BLE001 - MinIO raises several S3-compatible errors here
            return False
        return True

    def open_file(self, storage_key: str) -> tuple[BinaryIO, int | None]:
        if self.backend == "local":
            path = self.resolve_storage_key(storage_key)
            return path.open("rb"), path.stat().st_size

        response = self.minio_client.get_object(self.settings.minio_bucket, storage_key)
        size = None
        try:
            stat = self.minio_client.stat_object(self.settings.minio_bucket, storage_key)
            size = stat.size
        except Exception:  # noqa: BLE001 - stream can still be returned without size metadata
            pass
        return response, size

    def list_featured_images(self, limit: int = 12) -> list[dict]:
        if self.backend == "minio":
            objects = self.minio_client.list_objects(self.settings.minio_bucket, prefix="generated/", recursive=True)
            items = [
                {
                    "storage_key": item.object_name,
                    "file_size": item.size or 0,
                    "created_at": item.last_modified or datetime.now(timezone.utc),
                }
                for item in objects
                if item.object_name and is_image_key(item.object_name)
            ]
        else:
            generated_dir = self.root / "generated"
            if not generated_dir.exists():
                return []
            items = [
                {
                    "storage_key": path.relative_to(self.root).as_posix(),
                    "file_size": path.stat().st_size,
                    "created_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc),
                }
                for path in generated_dir.iterdir()
                if path.is_file() and is_image_key(path.name)
            ]

        items.sort(key=lambda item: item["created_at"], reverse=True)
        return items[:limit]

    @property
    def minio_client(self):
        if self._minio_client is None:
            try:
                from minio import Minio
            except ImportError as exc:
                raise RuntimeError("MinIO storage requires the 'minio' package. Run pip install -r requirements.txt.") from exc
            self._minio_client = Minio(
                self.settings.minio_endpoint,
                access_key=self.settings.minio_access_key,
                secret_key=self.settings.minio_secret_key,
                secure=self.settings.minio_secure,
            )
        return self._minio_client

    def ensure_bucket(self) -> None:
        client = self.minio_client
        if not client.bucket_exists(self.settings.minio_bucket):
            client.make_bucket(self.settings.minio_bucket)


def guess_content_type(suffix: str) -> str:
    suffix = suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    return "application/octet-stream"


def is_image_key(storage_key: str) -> bool:
    return Path(storage_key).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}


storage_service = StorageService()
