from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from tygle_drive.types.resources.files import File


class FileList(BaseModel):
    kind: Literal["drive#fileList"] = Field("drive#fileList")
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    files: Optional[List[File]] = Field(None)
    incomplete_search: Optional[bool] = Field(None, alias="incompleteSearch")
