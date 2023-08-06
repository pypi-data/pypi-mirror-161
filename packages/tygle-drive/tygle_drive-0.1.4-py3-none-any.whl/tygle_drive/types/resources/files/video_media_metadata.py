from typing import Optional

from pydantic import BaseModel, Field


class VideoMediaMetadata(BaseModel):
    width: Optional[int] = Field(None)
    height: Optional[int] = Field(None)
    duration_millis: Optional[int] = Field(None, alias="durationMillis")
