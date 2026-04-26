import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import httpx
from PIL import Image, ImageDraw, ImageFont


@dataclass
class SourceImage:
    path: Path
    mime_type: str
    filename: str


@dataclass
class ImageGenerationRequest:
    prompt: str
    model: str
    size: str
    quality: str
    output_format: str
    output_compression: int | None = None
    source_images: list[SourceImage] | None = None


@dataclass
class ImageGenerationResponse:
    image_bytes: bytes
    request_id: str
    elapsed_ms: int
    width: int
    height: int
    format: str


class ImageProvider:
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        raise NotImplementedError


class MockImageProvider(ImageProvider):
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        started_at = perf_counter()
        width, height = self._parse_size(request.size)
        image = Image.new("RGB", (width, height), (248, 250, 252))
        draw = ImageDraw.Draw(image)

        accent = (232, 93, 4)
        source_count = len(request.source_images or [])
        text = "MOYUAN MOCK\nIMAGE EDIT" if source_count else "MOYUAN MOCK\nAI IMAGE"
        prompt_preview = " ".join(request.prompt.split())[:180]

        draw.rectangle((0, 0, width, height), fill=(248, 250, 252))
        draw.rounded_rectangle(
            (width * 0.14, height * 0.14, width * 0.86, height * 0.86),
            radius=max(24, width // 28),
            fill=(255, 255, 255),
            outline=(226, 232, 240),
            width=max(2, width // 256),
        )
        draw.ellipse(
            (width * 0.39, height * 0.20, width * 0.61, height * 0.42),
            fill=accent,
        )
        font = ImageFont.load_default()
        if request.source_images:
            self._paste_source_preview(image, request.source_images[0].path)
        draw.multiline_text((width * 0.22, height * 0.48), text, fill=(15, 23, 42), font=font, spacing=10)
        draw.multiline_text(
            (width * 0.22, height * 0.62),
            f"sources: {source_count}\n{prompt_preview}",
            fill=(71, 85, 105),
            font=font,
            spacing=6,
        )

        buffer = BytesIO()
        image_format = "JPEG" if request.output_format == "jpeg" else request.output_format.upper()
        save_kwargs = {}
        if image_format == "JPEG":
            save_kwargs["quality"] = max(1, min(95, request.output_compression or 75))
        image.save(buffer, format=image_format, **save_kwargs)

        return ImageGenerationResponse(
            image_bytes=buffer.getvalue(),
            request_id=f"mock-{uuid4()}",
            elapsed_ms=int((perf_counter() - started_at) * 1000),
            width=width,
            height=height,
            format=request.output_format,
        )

    def _parse_size(self, value: str) -> tuple[int, int]:
        try:
            width, height = value.lower().split("x", 1)
            return int(width), int(height)
        except (ValueError, AttributeError):
            return 1024, 1024

    def _paste_source_preview(self, image: Image.Image, source_path: Path) -> None:
        width, height = image.size
        try:
            with Image.open(source_path) as source:
                source.thumbnail((int(width * 0.24), int(height * 0.24)))
                preview = source.convert("RGB")
                image.paste(preview, (int(width * 0.38), int(height * 0.18)))
        except OSError:
            return


class OpenAIImageProvider(ImageProvider):
    def __init__(self, api_key: str, base_url: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required when MOYUAN_IMAGE_PROVIDER=openai")

        started_at = perf_counter()
        output_format = request.output_format
        source_images = request.source_images or []
        if source_images:
            response = await self._create_edit(request, output_format, source_images)
        else:
            response = await self._create_generation(request, output_format)
        response.raise_for_status()
        body = response.json()

        try:
            image_base64 = body["data"][0]["b64_json"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("OpenAI image response did not include data[0].b64_json") from exc

        image_bytes = base64.b64decode(image_base64)
        width, height = self._parse_size(self._normalize_size(request.size))

        return ImageGenerationResponse(
            image_bytes=image_bytes,
            request_id=response.headers.get("x-request-id", ""),
            elapsed_ms=int((perf_counter() - started_at) * 1000),
            width=width,
            height=height,
            format=output_format,
        )

    async def _create_generation(self, request: ImageGenerationRequest, output_format: str) -> httpx.Response:
        payload: dict[str, object] = {
            "model": request.model,
            "prompt": request.prompt,
            "size": self._normalize_size(request.size),
            "quality": request.quality,
            "output_format": output_format,
        }
        if output_format in {"jpeg", "webp"} and request.output_compression is not None:
            payload["output_compression"] = request.output_compression

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            return await client.post(
                f"{self.base_url}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

    async def _create_edit(
        self,
        request: ImageGenerationRequest,
        output_format: str,
        source_images: list[SourceImage],
    ) -> httpx.Response:
        data: dict[str, str] = {
            "model": request.model,
            "prompt": request.prompt,
            "size": self._normalize_size(request.size),
            "quality": request.quality,
            "output_format": output_format,
        }
        if output_format in {"jpeg", "webp"} and request.output_compression is not None:
            data["output_compression"] = str(request.output_compression)

        file_handles = []
        try:
            files = []
            for source in source_images:
                file_handle = source.path.open("rb")
                file_handles.append(file_handle)
                files.append(("image", (source.filename, file_handle, source.mime_type)))

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                return await client.post(
                    f"{self.base_url}/images/edits",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    data=data,
                    files=files,
                )
        finally:
            for file_handle in file_handles:
                file_handle.close()

    def _normalize_size(self, value: str) -> str:
        size_map = {
            "1792x1024": "1536x1024",
            "1024x1792": "1024x1536",
        }
        return size_map.get(value, value)

    def _parse_size(self, value: str) -> tuple[int, int]:
        try:
            width, height = value.lower().split("x", 1)
            return int(width), int(height)
        except (ValueError, AttributeError):
            return 1024, 1024


def get_image_provider() -> ImageProvider:
    from app.core.config import get_settings

    settings = get_settings()
    if settings.image_provider == "openai":
        return OpenAIImageProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout_seconds=settings.generation_timeout_seconds,
        )
    return MockImageProvider()
