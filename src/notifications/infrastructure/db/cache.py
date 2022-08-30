import datetime
from abc import ABC, abstractmethod
from typing import Any

from notifications.types import seconds

from .redis import RedisClient


class BaseCache(ABC):
    """Базовый класс для реализации кэша."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Получение данных из кэша по заданному ключу."""

    @abstractmethod
    def set(self, key: str, data: Any, *, ttl: seconds | None = None, create_missing: bool = True) -> bool:
        """Сохранение данных с заданным ключом и параметрами.

        Args:
            key: ключ, по которому надо сохранять данные.
            data: данные для сохранения.
            ttl: значение ttl (время жизни) ключа, в секундах.
            create_missing: добавлять/обновлять запись с уже существующим ключом или нет.

        Returns:
            Были ли сохранены данные.
        """

    def get_ttl(self, ttl: seconds | datetime.timedelta | None = None) -> seconds | datetime.timedelta | None:
        """Получение `ttl` (таймаута) для записи в кэше."""
        if isinstance(ttl, datetime.timedelta):
            return ttl
        return None if ttl is None else max(0, int(ttl))


class RedisCache(BaseCache):
    """Кэш с использованием Redis."""

    def __init__(self, redis_client: RedisClient) -> None:
        assert isinstance(redis_client, RedisClient)
        self._redis_client = redis_client

    def get(self, key: str, /, *, default: Any | None = None) -> Any:
        return self._redis_client.get(key, default=default)

    def set(self, key: str, data: Any, *, ttl: seconds | None = None, create_missing: bool = True) -> bool:
        return self._redis_client.set(key, data, timeout=self.get_ttl(ttl), create_missing=create_missing)
