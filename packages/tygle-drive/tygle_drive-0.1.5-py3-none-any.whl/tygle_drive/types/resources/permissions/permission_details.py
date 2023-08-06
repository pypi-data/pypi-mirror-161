from typing import Optional

from pydantic import BaseModel, Field
from tygle_drive.types.enums.permissions.permission_details import PermissionType, Role


class PermissionDetails(BaseModel):
    permission_type: Optional[PermissionType] = Field(None, alias="permissionType")
    role: Optional[Role] = Field(None)
    inherited_from: Optional[str] = Field(None, alias="inheritedFrom")
    inherited: Optional[bool] = Field(None)
