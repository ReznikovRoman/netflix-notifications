import dataclasses
import datetime
import logging
import uuid
from typing import Callable, ClassVar

from notifications.core.config import CeleryQueue
from notifications.domain.messages import EmailNotificationService
from notifications.domain.messages.types import NotificationPayload
from notifications.domain.templates import TemplateService
from notifications.infrastructure.db.cache import BaseCache
from notifications.integrations.auth import NetflixAuthClient
from notifications.integrations.auth.types import BoundaryRegistrationDate, UserDetail
from notifications.integrations.ugc import NetflixUgcClient

from .enums import DefaultTemplateSlugs
from .exceptions import UnknownCeleryTaskError
from .repositories import TaskRepository
from .types import CeleryPeriodicTask, CeleryTask


@dataclasses.dataclass
class TaskService:
    """Сервис для работы с периодическими Celery задачами."""

    DEFAULT_DIGEST_LOCK: ClassVar[datetime.timedelta] = datetime.timedelta(hours=1)

    task_repository: TaskRepository
    email_service: EmailNotificationService
    template_service: TemplateService
    auth_client: NetflixAuthClient
    ugc_client: NetflixUgcClient

    key_factory: Callable[..., str]
    cache_client: BaseCache

    def get_all_registered(self) -> list[CeleryTask]:
        """Получение списка Celery задач для отображения в панели администратора."""
        return self.task_repository.get_all_registered()

    async def create_new_periodic(self, periodic_task: CeleryPeriodicTask, /) -> CeleryPeriodicTask:
        """Создание новой периодической задачи."""
        if not self.is_periodic_task_available(periodic_task.task):
            raise UnknownCeleryTaskError(f"Unknown Celery task <{periodic_task.task}>. Check if it is registered.")
        await self.template_service.get_by_slug(periodic_task.kwargs.get("template_slug"))
        return await self.task_repository.create_new_periodic(periodic_task)

    def is_periodic_task_available(self, target_task_name: str) -> bool:
        """Проверка доступности Celery задачи для использования."""
        for task in self.task_repository.get_all_registered_iter():
            if task.name == target_task_name:
                return True
        return False

    async def spawn_weekly_digest_tasks_by_boundary(self, dates_boundary: BoundaryRegistrationDate, /) -> None:
        """Создание фоновых задач на отправку дайджеста."""
        from .tasks import send_weekly_digest_to_subscriber

        await self._create_default_digest_template()
        for user in self.auth_client.get_users_within_registration_date_range_iter(dates_boundary):
            send_weekly_digest_to_subscriber.delay(user.dict())

    async def spawn_email_with_templates_tasks_by_boundary(
        self, dates_boundary: BoundaryRegistrationDate, /, *, template_slug: str, email_subject: str,
    ) -> None:
        """Создание фоновых задач на отправку одинаковых писем с заданным шаблоном."""
        from notifications.domain.messages.tasks import send_email

        for user in self.auth_client.get_users_within_registration_date_range_iter(dates_boundary):
            payload = self._build_template_payload(user, template_slug=template_slug, email_subject=email_subject)
            send_email.apply_async(args=[payload], queue=CeleryQueue.COMMON.value)

    async def send_digest_email_to_subscriber(self, user_data: UserDetail, /) -> None:
        """Отправка еженедельного дайджеста одному пользователю."""
        message_payload = self._build_digest_payload(user_data)
        await self._send_message_idempotently(message_payload)

    async def _send_message_idempotently(self, message_payload: NotificationPayload, /) -> None:
        """Идемпотентная отправка сообщения на почту.

        Пользователю не может отправиться уведомление с одинаковым заголовком в течение `DEFAULT_DIGEST_LOCK`.
        """
        subject = message_payload["subject"]
        email = message_payload["recipient_list"][0]
        key = self.key_factory(base_key=subject, prefix=f"periodic:digest:{email}:")
        if await self.cache_client.set(key, email, ttl=self.DEFAULT_DIGEST_LOCK, create_missing=False):
            await self.email_service.send_message(message_payload)
            return
        logging.info(f"[{key}] is locked. Email has been already sent.")

    async def _create_default_digest_template(self) -> None:
        """Создание шаблона уведомления для дайджеста."""
        await self.template_service.create_default_template(
            name="Weekly Digest", slug=DefaultTemplateSlugs.WEEKLY_DIGEST.value, filename="weekly_digest.html")

    def _build_digest_payload(self, user_data: UserDetail, /) -> NotificationPayload:
        """Формирование данных дайджеста для письма."""
        payload = NotificationPayload(
            subject="Еженедельный дайджест",
            recipient_list=[user_data.email],
            template_slug=DefaultTemplateSlugs.WEEKLY_DIGEST.value,
            context={
                "name": user_data.first_name,
                "recommendations": self._get_serialized_digest_recommendations(user_data.pk),
            },
        )
        return payload

    def _get_serialized_digest_recommendations(self, user_pk: uuid.UUID) -> list[dict]:
        """Получение сериализованных рекомендаций для дайджеста."""
        recommendations = [
            recommendation.dict()
            for recommendation in self.ugc_client.get_recommendations_for_user_iter(user_pk)
        ]
        return recommendations

    @staticmethod
    def _build_template_payload(
        user_data: UserDetail, /, *, template_slug: str, email_subject: str,
    ) -> NotificationPayload:
        """Формирование данных для отправки письма по шаблону."""
        payload = NotificationPayload(
            subject=email_subject,
            recipient_list=[user_data.email],
            template_slug=template_slug,
        )
        return payload
