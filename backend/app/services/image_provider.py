from dataclasses import dataclass
from io import BytesIO
from time import perf_counter
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont


@dataclass
class ImageGenerationRequest:
    prompt: str
    size: str
    quality: str
    output_format: str
    output_compression: int | None = None


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
        text = "MOYUAN MOCK\nAI IMAGE\n(no model call)"
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
        draw.multiline_text((width * 0.22, height * 0.48), text, fill=(15, 23, 42), font=font, spacing=10)
        draw.multiline_text((width * 0.22, height * 0.68), prompt_preview, fill=(71, 85, 105), font=font, spacing=6)

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


image_provider: ImageProvider = MockImageProvider()
