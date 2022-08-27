from enum import Enum


class DefaultRoles(str, Enum):
    """Роли в сервисе Netflix Auth по умолчанию."""

    VIEWERS = "viewers"
    SUBSCRIBERS = "subscribers"
