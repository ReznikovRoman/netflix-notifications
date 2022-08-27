from http import HTTPStatus

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends

from notifications.containers import Container
from notifications.domain.periodic_tasks import TaskService
from notifications.domain.periodic_tasks.types import CeleryPeriodicTask, CeleryTask

router = APIRouter(
    tags=["Dashboard"],
)


@router.get("/tasks", response_model=list[CeleryTask], summary="Список Celery задач")
@inject
async def get_registered_tasks(
    *,
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    """Получение списка зарегистрированных Celery задач, которые могут использовать администраторы."""
    return task_service.get_all_registered()


@router.post("/periodic-tasks", summary="Создание периодической задачи", status_code=HTTPStatus.NO_CONTENT)
@inject
async def create_new_periodic_task(
    periodic_task: CeleryPeriodicTask, *,
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    """Создание новой периодической задачи с отложенным запуском."""
    await task_service.create_new_periodic(periodic_task)
