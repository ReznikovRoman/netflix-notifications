from __future__ import annotations

import datetime
from functools import partial
from typing import TYPE_CHECKING

from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from celery_chunkificator.chunkify import DateChunk, chunkify_task
from dependency_injector.wiring import Provide, inject

from notifications.containers import Container
from notifications.core.config import CeleryQueue
from notifications.helpers import TZ_MOSCOW, sync_task
from notifications.integrations.auth.enums import DefaultRoles
from notifications.integrations.auth.types import BoundaryRegistrationDate, UserDetail

from .constants import PERIODIC_TASK_PREFIX
from .types import UserPayload

if TYPE_CHECKING:
    from notifications.celery import Task
    from notifications.integrations.auth import NetflixAuthClient

    from .services import TaskService


@inject
def get_date_boundaries(
    user_role: str | None = None, *, auth_client: NetflixAuthClient = Provide[Container.auth_client],
) -> BoundaryRegistrationDate:
    """Получение граничных дат с опциональной фильтрацией по ролям пользователей."""
    if user_role is None:
        return auth_client.get_boundary_registration_dates()
    return auth_client.get_boundary_registration_dates(user_role=DefaultRoles(user_role))


def get_users_initial_chunk(*args, user_role: DefaultRoles | None = None, **kwargs) -> DateChunk:
    """Получение начального чанка дат, основанного на первой и последней датах регистрации."""
    date_boundaries = get_date_boundaries(user_role=user_role)
    chunk = DateChunk(
        start=date_boundaries.first_registration_date,
        size=datetime.timedelta(days=30),
        max=date_boundaries.last_registration_date,
    )
    return chunk


get_subscribers_initial_chunk = partial(get_users_initial_chunk, user_role=DefaultRoles.SUBSCRIBERS.value)


@shared_task(
    queue=CeleryQueue.COMMON.value,
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
async def send_weekly_digest_to_subscriber(
    self: Task,
    user_payload: UserPayload, *args,
    task_service: TaskService = Provide[Container.task_service],
    **kwargs,
) -> None:
    """Фоновая задача по отправке еженедельного дайджеста одному подписчику."""
    user_payload["registration_date"] = user_payload["registration_date"].rsplit("T")[0]
    await task_service.send_digest_email_to_subscriber(UserDetail(**user_payload))
    self.log.debug(f"Email has been sent to <{user_payload['email']}>.")


@shared_task(
    queue=CeleryQueue.COMMON.value,
    bind=True,
    serializer="pickle",
    ignore_result=True,
    time_limit=2 * 60 * 60,
    soft_time_limit=60 * 60,
    expires=datetime.datetime.now(TZ_MOSCOW) + datetime.timedelta(days=1),
    lock_ttl=3 * 60 * 60,
)
@chunkify_task(
    sleep_timeout=10,
    initial_chunk=get_subscribers_initial_chunk,
)
@sync_task
@inject
async def send_weekly_digest_to_subscribers(
    self: Task,
    chunk: DateChunk, *args,
    task_service: TaskService = Provide[Container.task_service],
    **kwargs,
) -> None:
    """Фоновая задача по рассылке еженедельного дайджеста всем подписчикам."""
    start, end = chunk.range
    dates_boundary = BoundaryRegistrationDate(first_registration_date=start, last_registration_date=end)
    await task_service.spawn_weekly_digest_tasks_by_boundary(dates_boundary)
    self.log.debug("Spawned new `digest` tasks.")


@shared_task(
    name=f"{PERIODIC_TASK_PREFIX}periodic_tasks.tasks.send_emails_with_template",
    queue=CeleryQueue.COMMON.value,
    bind=True,
    serializer="pickle",
    ignore_result=True,
    time_limit=2 * 60 * 60,
    soft_time_limit=60 * 60,
    expires=datetime.datetime.now(TZ_MOSCOW) + datetime.timedelta(days=1),
    lock_ttl=3 * 60 * 60,
)
@chunkify_task(
    sleep_timeout=10,
    initial_chunk=get_users_initial_chunk,
)
@sync_task
@inject
async def send_emails_with_template(
    self: Task,
    chunk: DateChunk,
    template_slug: str, email_subject: str, *args,
    task_service: TaskService = Provide[Container.task_service],
    **kwargs,
) -> None:
    """Фоновая задача по рассылке еженедельного дайджеста всем подписчикам."""
    start, end = chunk.range
    dates_boundary = BoundaryRegistrationDate(first_registration_date=start, last_registration_date=end)
    await task_service.spawn_email_with_templates_tasks_by_boundary(
        dates_boundary, template_slug=template_slug, email_subject=email_subject)
    self.log.debug("Spawned new `template` tasks.")


send_weekly_digest_to_subscribers: Task
send_weekly_digest_to_subscriber: Task
