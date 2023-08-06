from enum import Enum


class DisplayName(str, Enum):
    USER = "user"
    GROUP = "group"
    DOMAIN = "domain"
    ANYONE = "anyone"
