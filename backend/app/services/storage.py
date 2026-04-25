from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings


class StorageService:
    def __init__(self) -> None:
        self.root = get_settings().storage_dir

    def ensure_directories(self) -> None:
        for name in ["assets", "generated", "thumbnails", "exports"]:
            (self.root / name).mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile, asset_type: str) -> dict:
        self.ensure_directories()
        suffix = Path(file.filename or "upload.bin").suffix or ".bin"
        filename = f"{uuid4().hex}{suffix}"
        relative_path = Path("assets") / asset_type / filename
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        path.write_bytes(content)
        return self.describe_file(path, relative_path)

    def save_generated_bytes(self, content: bytes, suffix: str = ".jpg") -> dict:
        self.ensure_directories()
        filename = f"{uuid4().hex}{suffix}"
        relative_path = Path("generated") / filename
        path = self.root / relative_path
        path.write_bytes(content)
        return self.describe_file(path, relative_path)

    def save_thumbnail(self, source_path: Path, suffix: str = ".jpg") -> dict:
        self.ensure_directories()
        filename = f"{uuid4().hex}{suffix}"
        relative_path = Path("thumbnails") / filename
        path = self.root / relative_path
        with Image.open(source_path) as image:
            image.thumbnail((384, 384))
            image.convert("RGB").save(path, format="JPEG", quality=82)
        return self.describe_file(path, relative_path)

    def describe_file(self, path: Path, relative_path: Path) -> dict:
        content = path.read_bytes()
        width = None
        height = None
        try:
            with Image.open(path) as image:
                width, height = image.size
        except UnidentifiedImageError:
            pass
        return {
            "path": path,
            "storage_key": relative_path.as_posix(),
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


storage_service = StorageService()
