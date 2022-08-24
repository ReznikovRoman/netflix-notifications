import enum


class NotificationType(str, enum.Enum):
    """Тип уведомления."""

    EMAIL = "email"


class NotificationPriority(str, enum.Enum):
    """Приоритет уведомления."""

    URGENT = "urgent"
    EMAILS = "emails"
    DEFAULT = "default"
