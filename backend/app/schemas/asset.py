from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

AssetType = Literal[
    "product_source",
    "reference_image",
    "brand_asset",
    "generated_image",
    "thumbnail",
    "export_zip",
]


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    product_id: str | None = None
    asset_type: AssetType
    storage_key: str
    url: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    file_size: int
    checksum: str
    created_at: datetime


class FeaturedImageRead(BaseModel):
    storage_key: str
    url: str
    file_size: int
    created_at: datetime
