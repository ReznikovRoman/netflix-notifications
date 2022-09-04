from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from notifications.domain.templates import TemplateService
from notifications.infrastructure.emails.clients import BaseEmailClient, EmailMessageDetail

from .types import NotificationPayload

if TYPE_CHECKING:
    from notifications.types import seconds


class BaseNotificationService(ABC):
    """Базовый сервис по отправке уведомлений."""

    DEFAULT_NOTIFICATION_LOCK: ClassVar[seconds | datetime.timedelta]

    _template_service: TemplateService

    @abstractmethod
    async def send_message(self, message_payload: NotificationPayload, /) -> int:
        """Отправка уведомления пользователю."""

    @abstractmethod
    async def build_message_from_payload(self, payload: NotificationPayload, /) -> EmailMessageDetail:
        """Построение сообщения на основе данных из очереди."""

    async def _get_message_content_from_payload(self, payload: NotificationPayload, /) -> str:
        """Получение текста сообщения на основе данных из очереди."""
        content = payload.get("content")
        if content is not None:
            return content
        template_slug = payload["template_slug"]
        return await self._get_template_content_by_slug(template_slug, context=payload.get("context", {}))

    async def _get_template_content_by_slug(self, slug: str, /, *, context: dict[str, Any]) -> str:
        """Получение текста сообщения после рендера шаблона."""
        template = await self._template_service.get_by_slug(slug)
        return await self._template_service.render_template_from_string(template.content, context=context)


class EmailNotificationService(BaseNotificationService):
    """Сервис по отправке уведомлений на почту."""

    DEFAULT_NOTIFICATION_LOCK = datetime.timedelta(hours=1)

    def __init__(self, email_client: BaseEmailClient, template_service: TemplateService) -> None:
        assert isinstance(email_client, BaseEmailClient)
        self._email_client = email_client

        assert isinstance(template_service, TemplateService)
        self._template_service = template_service

    async def send_message(self, message_payload: NotificationPayload, /) -> int:
        message = await self.build_message_from_payload(message_payload)
        return self._email_client.send_messages((message,))

    async def build_message_from_payload(self, payload: NotificationPayload, /) -> EmailMessageDetail:
        content = await self._get_message_content_from_payload(payload)
        message = EmailMessageDetail(
            subject=payload["subject"],
            content=content,
            recipient_list=payload["recipient_list"],
        )
        return message
