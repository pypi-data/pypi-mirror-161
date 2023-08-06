from typing import Literal, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    kind: Literal["drive#user"] = Field("drive#user")
    display_name: Optional[str] = Field(None, alias="displayName")
    photo_link: Optional[str] = Field(None, alias="photoLink")
    me: Optional[bool] = Field(None)
    permission_id: Optional[str] = Field(None, alias="permissionId")
    email_address: Optional[str] = Field(None, alias="emailAddress")
