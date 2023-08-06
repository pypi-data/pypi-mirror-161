from typing import ClassVar, Dict, Optional

from pydantic import Field
from tygle.base import Resource
from tygle_drive.types.enums.files import AnyMimeType


class ShortcutDetails(Resource):
    target_id: Optional[str] = Field(None, alias="targetId")
    taget_mime_type: Optional[AnyMimeType] = Field(None, alias="targetMimeType")
