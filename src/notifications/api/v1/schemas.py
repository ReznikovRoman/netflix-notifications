from typing import Any

from pydantic import BaseModel, EmailStr, Field, root_validator

from notifications.domain.messages.enums import NotificationPriority, NotificationType
from notifications.domain.messages.types import Queue

from .exceptions import MissingContentError


class NotificationIn(BaseModel):
    """Новое уведомление от внешнего сервиса."""

    subject: str
    notification_type: NotificationType
    priority: NotificationPriority
    recipient_list: list[EmailStr]
    content: str | None = None
    template_slug: str | None = None
    context: dict[str, Any] | None = Field(default_factory=dict)

    @root_validator(pre=True)
    def clean_content_with_slug(cls, values: dict) -> dict:
        """Проверка контента и слага уведомления.

        Если клиент решает использовать готовый шаблон с слагом `template_slug`, то поле `content` не используется.

        Если шаблон не выбран, то клиент должен обязательно добавить текст в поле `content`.
        """
        content = values.get("content")
        template_slug = values.get("template_slug")
        if template_slug is not None:
            values["content"] = None
            return values
        if content is None:
            raise MissingContentError()
        return values


class NotificationShortDetails(BaseModel):
    """Короткая информация об уведомлении."""

    notification_id: str
    queue: Queue


class TemplateIn(BaseModel):
    """Новый шаблон."""

    name: str
    slug: str
    content: str


class TemplateList(BaseModel):
    """Список шаблонов."""

    name: str
    slug: str


class TemplateUpdate(BaseModel):
    """Обновление шаблона."""

    name: str | None
    content: str | None
