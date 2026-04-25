from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

GenerationTaskStatus = Literal["created", "queued", "running", "succeeded", "failed", "cancelled", "expired"]
ImageType = Literal[
    "main_image",
    "lifestyle_scene",
    "detail_image",
    "detail_set",
    "campaign",
    "social_post",
    "variant_batch",
]
ImageQuality = Literal["low", "medium", "high"]
OutputFormat = Literal["jpeg", "png", "webp"]


class GenerationInputParams(BaseModel):
    platform: str | None = None
    aspect_ratio: str | None = "1:1"
    size: str = "1024x1024"
    quality: ImageQuality = "low"
    output_format: OutputFormat = "jpeg"
    output_compression: int | None = Field(default=50, ge=0, le=100)
    prompt: str | None = None
    background: str | None = None
    style: str | None = None
    lighting: str | None = None
    composition: str | None = None
    scene: str | None = None
    include_text: bool = False
    text_requirements: str | None = None


class GenerationTaskCreate(BaseModel):
    project_id: str
    product_id: str | None = None
    image_type: ImageType = "main_image"
    template_id: str | None = None
    source_asset_ids: list[str] = Field(default_factory=list)
    params: GenerationInputParams = Field(default_factory=GenerationInputParams)
    negative_constraints: list[str] = Field(default_factory=list)
    count: int = Field(default=1, ge=1, le=50)


class GenerationTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    product_id: str | None = None
    created_by: str
    status: GenerationTaskStatus
    image_type: ImageType
    template_id: str | None = None
    template_version: int | None = None
    input_params: dict[str, Any]
    rendered_prompt: str
    model: str
    model_params: dict[str, Any]
    error_code: str | None = None
    error_message: str | None = None
    request_id: str | None = None
    elapsed_ms: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class GenerationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    asset_id: str
    thumbnail_asset_id: str | None = None
    url: str
    thumbnail_url: str | None = None
    width: int
    height: int
    format: str
    is_favorite: bool = False
    score: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
