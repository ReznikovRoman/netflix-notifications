import enum


class NotificationType(str, enum.Enum):
    """Тип уведомления."""

    EMAIL = "email"


class NotificationPriority(str, enum.Enum):
    """Приоритет уведомления."""

    URGENT = "urgent"
    COMMON = "common"
    DEFAULT = "default"
