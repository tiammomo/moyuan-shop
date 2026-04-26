from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "production"]
ImageProviderName = Literal["mock", "openai"]
ImageQuality = Literal["low", "medium", "high"]
OutputFormat = Literal["jpeg", "png", "webp"]


class Settings(BaseSettings):
    app_name: str = "moyuan-shop-api"
    app_version: str = "0.1.0"
    environment: Environment = "development"
    debug: bool = True
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])

    storage_dir: Path = Path("storage")
    public_asset_base_url: str | None = None

    image_provider: ImageProviderName = "mock"
    default_model: str = "gpt-image-2"
    default_size: str = "1024x1024"
    default_quality: ImageQuality = "low"
    default_output_format: OutputFormat = "jpeg"
    default_output_compression: int = Field(default=50, ge=0, le=100)
    generation_timeout_seconds: int = Field(default=900, ge=1)
    max_generation_count: int = Field(default=4, ge=1, le=50)

    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("OPENAI_BASE_URL", "MOYUAN_OPENAI_BASE_URL"),
    )
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "MOYUAN_OPENAI_API_KEY"),
    )

    database_url: str = "sqlite:///./moyuan_shop.db"
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_prefix="MOYUAN_", env_file=".env", extra="ignore")

    @field_validator("api_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        if not value.startswith("/"):
            value = f"/{value}"
        return value.rstrip("/") or "/api"

    @field_validator("public_asset_base_url")
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        return value or None


@lru_cache
def get_settings() -> Settings:
    return Settings()
