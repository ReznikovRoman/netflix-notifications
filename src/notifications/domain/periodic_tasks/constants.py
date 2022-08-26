from typing import Final

# Префикс задач, которые используются внутри фреймворка Celery.
CELERY_INTERNAL_TASK_PREFIX = "celery."

# Префикс, обозначающий периодическую задачу. Задачи с таким префиксом могут использовать в панели администратора.
PERIODIC_TASK_PREFIX: Final[str] = "periodic."
