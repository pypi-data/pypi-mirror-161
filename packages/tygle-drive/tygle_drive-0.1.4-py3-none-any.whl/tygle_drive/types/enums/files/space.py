from enum import Enum


class Space(str, Enum):
    DRIVE = "drive"
    APP_DATA_FOLDER = "appDataFolder"
    PHOTOS = "photos"
