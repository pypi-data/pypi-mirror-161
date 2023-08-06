from typing import Literal, Optional

from pydantic import Field
from tygle.base import Resource
from tygle_drive.types.enums.permissions import DisplayName, Role, Type

from .permission_details import PermissionDetails


class Permission(Resource):
    kind: Literal["drive#permission"] = Field("drive#permission")
    id: Optional[str] = Field(None)
    type: Optional[Type] = Field(None)
    email_address: Optional[str] = Field(None, alias="emailAddress")
    domain: Optional[str] = Field(None)
    role: Optional[Role] = Field(None)
    allow_file_discovery: Optional[bool] = Field(None, alias="allowFileDiscovery")
    display_name: Optional[DisplayName] = Field(None, alias="displayName")
    photo_link: Optional[str] = Field(None, alias="photoLink")
    expiration_time: Optional[str] = Field(None, alias="expirationTime")
    deleted: Optional[bool] = Field(None)
    permission_details: Optional[PermissionDetails] = Field(
        None, alias="permissionDetails"
    )
    view: Optional[str] = Field(None)
    pending_owner: Optional[bool] = Field(None, alias="pendingOwner")
