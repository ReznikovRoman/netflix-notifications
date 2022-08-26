import json
from contextlib import AbstractAsyncContextManager
from typing import Callable, Iterator

from celery import Celery
from celery_sqlalchemy_scheduler.models import CrontabSchedule, PeriodicTask
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from notifications.common.exceptions import ConflictError

from .constants import PERIODIC_TASK_PREFIX
from .types import CeleryPeriodicTask, CeleryTask


class TaskRepository:
    """Репозиторий для работы с Celery задачами."""

    def __init__(
        self,
        celery_app: Celery,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]] = None,
    ) -> None:
        self._celery_app = celery_app
        self._session_factory = session_factory

    def get_all_registered_iter(self) -> Iterator[CeleryTask]:
        """Получение списка зарегистрированных задач.

        Возвращает итератор.
        """
        for task in self._celery_app.tasks.keys():
            task: str
            if task.startswith(PERIODIC_TASK_PREFIX):
                yield CeleryTask(name=task)

    def get_all_registered(self) -> list[CeleryTask]:
        """Получение списка зарегистрированных задач."""
        return list(self.get_all_registered_iter())

    async def create_new_periodic(self, periodic_task: CeleryPeriodicTask, /) -> PeriodicTask:
        """Создание и регистрация новой периодической задачи."""
        async with self._session_factory() as session:
            schedule = CrontabSchedule(**periodic_task.crontab.dict())
            periodic_task = PeriodicTask(
                crontab=schedule,
                kwargs=json.dumps(periodic_task.kwargs),
                **periodic_task.dict(exclude={"crontab", "kwargs"}),
            )
            session.add(periodic_task)
            try:
                await session.commit()
                return periodic_task
            except IntegrityError:
                raise ConflictError(f"Task <{periodic_task.task}> already exists.")
