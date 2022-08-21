from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Callable, ClassVar

import redis
from celery import Celery
from celery.app.task import Task as _Task
from celery.utils.log import get_task_logger

from notifications.core.config import CelerySettings, get_settings

if TYPE_CHECKING:
    from celery.result import AsyncResult

    from .types import seconds

settings = get_settings()

redis_client = redis.Redis.from_url(settings.REDIS_CELERY_URL)


celery_config = {
    "broker_url": settings.CELERY_BROKER_URL,
    "result_backend": settings.CELERY_RESULT_BACKEND,
    "beat_dburi": settings.DB_URL,
}
app = Celery(
    main="notifications",
    task_cls="notifications.celery:Task",
)
app.config_from_object(obj=CelerySettings, namespace="CELERY")
app.autodiscover_tasks()
app.conf.update(celery_config)


# CELERY PERIODIC TASKS
# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html
app.conf.beat_schedule = {}


class Task(_Task):
    """Переопределенная задача `celery.Task` для установки лока."""

    # ttl лока в секундах
    lock_ttl: ClassVar[seconds | None] = None

    # уникальный суффикс лока: None, tuple или callable, возвращающий tuple
    lock_suffix: ClassVar[tuple | Callable[..., tuple] | None] = None

    log = get_task_logger(__name__)

    def __call__(self, *args, **kwargs):
        self.log.info(f"Starting task {self.request.id}")
        return super().__call__(*args, **kwargs)

    def get_lock_key(self, args, kwargs) -> str:
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
            redis_client.set(lock_key, timestamp, ex=self.lock_ttl)
            return True
        elif not redis_client.set(lock_key, timestamp, ex=self.lock_ttl, nx=True):
            self.log.debug(f"[{lock_key}] is locked")
            return False
        self.log.debug(f"[{lock_key}] has been acquired")
        return True

    def delay(self, *args, force: bool = False, **kwargs) -> AsyncResult | None:
        if not self.lock_ttl:
            return super().apply_async(args, kwargs)
        lock_key = self.get_lock_key(args, kwargs)
        if self.acquire_lock(lock_key, force=force):
            return super().apply_async(args, kwargs)
        return None

    def apply_async(self, args=None, kwargs=None, *, force: bool = False, **options) -> AsyncResult | None:
        if not self.lock_ttl:
            return super().apply_async(args=args, kwargs=kwargs, **options)
        lock_key = self.get_lock_key(args, kwargs)
        if self.acquire_lock(lock_key, force=force):
            return super().apply_async(args=args, kwargs=kwargs, **options)
        return None
