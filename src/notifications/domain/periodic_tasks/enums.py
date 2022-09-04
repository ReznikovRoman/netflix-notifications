from enum import Enum


class DefaultTemplateSlugs(str, Enum):
    """Слаги шаблонов по умолчанию."""

    WEEKLY_DIGEST = "_notifications-weekly_digest"


class NotificationSubject(str, Enum):
    """Заголовки уведомлений."""

    WEEKLY_DIGEST = "Еженедельный дайджест"
