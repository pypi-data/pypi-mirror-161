from enum import Enum


class Role(str, Enum):
    OWNER = "owner"
    ORGANIZER = "organizer"
    FILE_ORGANIZER = "fileOrganizer"
    WRITER = "writer"
    COMMENTER = "commenter"
    READER = "reader"
