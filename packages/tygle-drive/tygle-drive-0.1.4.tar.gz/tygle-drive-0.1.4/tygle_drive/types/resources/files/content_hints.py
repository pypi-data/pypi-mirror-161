from typing import ClassVar, Dict, Optional

from pydantic import BaseModel, Field
from tygle_drive.types.enums.files import ExportMimeType


class Thumbnail(BaseModel):
    image: Optional[bytes] = Field(None)
    mime_type: Optional[ExportMimeType] = Field(None, alias="mimeType")


class ContentHints(BaseModel):
    thumbnail: Optional[Thumbnail] = Field(None)
    indexable_text: Optional[str] = Field(None, alias="indexableText")
