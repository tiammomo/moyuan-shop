from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/image-generation")
def get_image_generation_settings() -> dict:
    settings = get_settings()
    return {
        "data": {
            "default_model": settings.default_model,
            "default_size": settings.default_size,
            "default_quality": settings.default_quality,
            "default_output_format": settings.default_output_format,
            "default_output_compression": settings.default_output_compression,
            "generation_timeout_seconds": settings.generation_timeout_seconds,
            "max_generation_count": settings.max_generation_count,
            "image_provider": settings.image_provider,
            "poll_interval_seconds": 3,
        }
    }
