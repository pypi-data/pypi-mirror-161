from enum import Enum


class Type(str, Enum):
    USER = "user"
    GROUP = "group"
    DOMAIN = "domain"
    ANYONE = "anyone"
