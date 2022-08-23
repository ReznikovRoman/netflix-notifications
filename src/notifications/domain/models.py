from abc import ABC

from aredis_om import HashModel
from orjson import orjson

from notifications.core.config import get_settings

settings = get_settings()


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class BaseHashModel(HashModel, ABC):
    """Базовая модель типа `HashModel` сервиса."""

    class Meta:
        global_key_prefix = settings.REDIS_KEY_PREFIX

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
