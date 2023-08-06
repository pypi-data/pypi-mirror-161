from enum import Enum


class PermissionType(str, Enum):
    FILE = "file"
    MEMBER = "member"
