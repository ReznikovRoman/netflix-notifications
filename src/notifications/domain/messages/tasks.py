from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from dependency_injector.wiring import Provide, inject

from notifications.containers import Container
from notifications.helpers import TZ_MOSCOW, sync_task

if TYPE_CHECKING:
    from notifications.celery import Task

    from .services import EmailNotificationService
    from .types import NotificationPayload


@shared_task(
    bind=True,
    ignore_result=True,
    time_limit=5,
    soft_time_limit=3,
    default_retry_delay=5,
    autoretry_for=(SoftTimeLimitExceeded,),
    expires=datetime.datetime.now(TZ_MOSCOW) + datetime.timedelta(hours=12),
)
@sync_task
@inject
async def send_email(
    self: Task,
    notification: NotificationPayload, *args,
    email_service: EmailNotificationService = Provide[Container.email_notification_service],
    **kwargs,
) -> None:
    """Фоновая задача по отправке уведомления на почту."""
    # TODO [Дипломный проект]: Сделать задачу идемпотентной -> сохранять информацию об отправке уведомления
    await email_service.send_message(notification)
    self.log.info("Notification has been sent.")


send_email: Task
