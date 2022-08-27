from typing import Any, Sequence, TypedDict

from typing_extensions import NotRequired

Queue = str


class NotificationPayload(TypedDict):
    """Сериализованное уведомление."""

    subject: str
    recipient_list: Sequence[str]
    content: NotRequired[str]
    template_slug: NotRequired[str]
    context: NotRequired[dict[str, Any]]
