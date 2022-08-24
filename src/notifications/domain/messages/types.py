from typing import Any, TypedDict

Queue = str


class NotificationPayload(TypedDict):
    """Сериализованное уведомление."""

    subject: str
    notification_type: str
    recipient_list: list[str]
    content: str | None
    template_slug: str | None
    context: dict[str, Any] | None
