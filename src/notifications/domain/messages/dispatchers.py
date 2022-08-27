from notifications.api.v1.schemas import NotificationIn, NotificationShortDetails
from notifications.core.config import CeleryQueue
from notifications.domain.templates import TemplateService

from .enums import NotificationPriority, NotificationType
from .exceptions import InvalidNotificationTypeError
from .services import EmailNotificationService
from .types import NotificationPayload, Queue


class NotificationDispatcherService:
    """Сервис для распределения уведомлений по сервисам и очередям."""

    def __init__(self, email_service: EmailNotificationService, template_service: TemplateService) -> None:
        assert isinstance(email_service, EmailNotificationService)
        self._email_service = email_service

        assert isinstance(template_service, TemplateService)
        self._template_service = template_service

    async def dispatch_notification(self, notification: NotificationIn, /) -> NotificationShortDetails:
        """Перенаправление уведомления в очередь для дальнейшей отправки пользователю."""
        from .tasks import send_email

        if template_slug := notification.template_slug:
            await self.check_if_template_exists(template_slug)
        notification_type = self._clean_notification_type(notification.notification_type)
        queue = self._select_queue_by_priority(notification.priority)
        match notification_type:
            case NotificationType.EMAIL:
                result = send_email.apply_async(args=[self._build_payload(notification)], queue=queue)
            case _:
                raise InvalidNotificationTypeError(message=f"Invalid notification type <{notification_type}>")
        return NotificationShortDetails(notification_id=result.id, queue=queue)

    async def check_if_template_exists(self, template_slug: str, /) -> None:
        """Проверка существования шаблона с данным слагом."""
        await self._template_service.get_by_slug(template_slug)

    @staticmethod
    def _build_payload(notification: NotificationIn, /) -> NotificationPayload:
        """Формирование данных для отправки в очередь Celery."""
        data = notification.dict(exclude={"priority", "notification_type"})
        return data

    @staticmethod
    def _select_queue_by_priority(priority: str, /) -> Queue:
        """Выбор очереди, в которую попадет уведомление для дальнейшей обработки."""
        try:
            current_priority = NotificationPriority(priority).value
        except ValueError:
            current_priority = NotificationPriority.DEFAULT.value
        priority_queue_map = {
            NotificationPriority.DEFAULT.value: CeleryQueue.DEFAULT.value,
            NotificationPriority.COMMON.value: CeleryQueue.COMMON.value,
            NotificationPriority.URGENT.value: CeleryQueue.URGENT_NOTIFICATIONS.value,
        }
        return priority_queue_map[current_priority]

    @staticmethod
    def _clean_notification_type(notification_type: str, /) -> NotificationType:
        """Проверка типа уведомления на доступность."""
        try:
            return NotificationType(notification_type)
        except ValueError:
            raise InvalidNotificationTypeError(message=f"Invalid notification type <{notification_type}>")
