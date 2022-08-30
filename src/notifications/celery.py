from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Sequence

from celery import Celery
from celery.app.task import Task as _Task
from celery.result import AsyncResult
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from dependency_injector.wiring import Provide

from notifications.core.config import CelerySettings, get_settings

from .containers import Container

if TYPE_CHECKING:
    from notifications.infrastructure.db.cache import BaseCache

    from .types import seconds

settings = get_settings()


class Task(_Task):
    """Переопределенная Celery задача для установки лока."""

    cache_client: BaseCache = Provide[Container.cache_client]

    # ttl лока в секундах
    lock_ttl: ClassVar[seconds | None] = None

    # уникальный суффикс лока: None, tuple или callable, возвращающий tuple
    lock_suffix: ClassVar[tuple | Callable[..., tuple] | None] = None

    log = get_task_logger(__name__)

    def __call__(self, *args, **kwargs):
        self.log.info(f"Starting task {self.request.id}")
        return super().__call__(*args, **kwargs)

    def get_lock_key(self, args: Sequence[Any], kwargs: dict[str, Any]) -> str:
        """Получение ключа блокировки для сохранения в БД."""
        if lock_suffix := self.__class__.lock_suffix:
            if callable(lock_suffix):
                lock_suffix = lock_suffix(*args or (), **kwargs or {})
        else:
            lock_suffix = ()
        return ":".join(("task", self.name, *map(str, lock_suffix), "lock"))

    def acquire_lock(self, lock_key: str, *, force: bool = False) -> bool:
        """Установка и проверка блокировки на фоновую задачу."""
        timestamp = datetime.datetime.now().timestamp()
        if force:
            self.log.debug(f"force=True, ignoring [{lock_key}]")
            self.cache_client.set(lock_key, timestamp, ttl=self.lock_ttl)
            return True
        elif not self.cache_client.set(lock_key, timestamp, ttl=self.lock_ttl, create_missing=False):
            self.log.debug(f"[{lock_key}] is locked")
            return False
        self.log.debug(f"[{lock_key}] has been acquired")
        return True

    def delay(self, *args, force: bool = False, **kwargs) -> AsyncResult:
        if not self.lock_ttl or "chunk" in kwargs:
            return super().apply_async(args, kwargs)
        lock_key = self.get_lock_key(args, kwargs)
        if self.acquire_lock(lock_key, force=force):
            return super().apply_async(args, kwargs)
        return AsyncResult(id="-1")

    def apply_async(
        self,
        args: Sequence[Any] | None = None, kwargs: dict[str, Any] | None = None, *,
        force: bool = False,
        **options,
    ) -> AsyncResult:
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        if not self.lock_ttl or "chunk" in kwargs:
            return super().apply_async(args=args, kwargs=kwargs, **options)
        lock_key = self.get_lock_key(args, kwargs)
        if self.acquire_lock(lock_key, force=force):
            return super().apply_async(args=args, kwargs=kwargs, **options)
        return AsyncResult(id="-1")


def create_celery() -> Celery:
    """Создание приложения Celery."""
    celery_config = {
        "broker_url": settings.CELERY_BROKER_URL,
        "result_backend": settings.CELERY_RESULT_BACKEND,
        "beat_dburi": settings.BEAT_DB_URL,
    }
    app = Celery(
        main="notifications",
        task_cls="notifications.celery:Task",
    )
    app.config_from_object(obj=CelerySettings)
    app.autodiscover_tasks(
        packages=[
            "notifications.domain.messages",
        ],
    )
    app.conf.update(celery_config)

    # CELERY PERIODIC TASKS
    # https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html
    app.conf.beat_schedule = {
        # Рассылка еженедельного дайджеста подписчикам
        "send_weekly_digest": {
            "task": "notifications.domain.periodic_tasks.tasks.send_weekly_digest_to_subscribers",
            "schedule": crontab(hour="19", minute="0", day_of_week="5"),
        },
    }

    return app
