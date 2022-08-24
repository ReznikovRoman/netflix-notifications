import asyncio
import functools
import re
from typing import Any, Awaitable, Callable, Coroutine, Iterator
from zoneinfo import ZoneInfo

SLUG_REGEX = re.compile(r"^[-\w]+$")

TZ_MOSCOW = ZoneInfo("Europe/Moscow")

sentinel: Any = object()


def delay_tasks(*tasks: Coroutine) -> None:
    """Вспомогательная функция для запуска задач в фоне.

    Для надежной работы нужно сохранять ссылку на функцию.
    https://docs.python.org/3/library/asyncio-task.html#creating-tasks
    """
    background_tasks = set()
    for _task in tasks:
        task = asyncio.create_task(_task)
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)


def resolve_callables(mapping: dict) -> Iterator[tuple[Any, Any]]:
    """Генерация пар ключ-значение из `mapping`, где значения могут быть callable объектами."""
    for key, value in mapping.items():
        yield key, value() if callable(value) else value


def sync_task(func: Callable[..., Awaitable]) -> Callable:
    """Декоратор для запуска celery задач в текущем event loop'е."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))

    return wrapper
