import base64
import datetime
import hashlib
from abc import ABC, abstractmethod
from typing import Any

from notifications.types import seconds

from .redis import RedisClient, SyncRedisClient


class CacheKeyBuilder:
    """Генератор ключей для кэша."""

    @classmethod
    def make_key(
        cls, key_to_hash: str, *, min_length: int, prefix: str | None = None, suffix: str | None = None,
    ) -> str:
        """Получение ключа для кэша.

        Хэшируем исходной ключ `key_to_hash` - используем первые `min_length` символов из полученного хеша.
        При необходимости добавляем префикс и суффикс.
        """
        hashed_key = cls.make_hash(key_to_hash, length=min_length)
        key = cls.make_key_with_affixes(hashed_key, prefix, suffix)
        return key

    @staticmethod
    def make_hash(string: str, /, *, length: int) -> str:
        """Хеширование строки с заданной длиной."""
        hashed_string = hashlib.sha256(string.encode())
        hash_str = base64.urlsafe_b64encode(hashed_string.digest()).decode("ascii")
        return hash_str[:length]

    @staticmethod
    def make_key_with_affixes(base: str, prefix: str | None = None, suffix: str | None = None) -> str:
        """Создание ключа с опциональными префиксом и суффиксом."""
        key = base
        if prefix is not None:
            prefix = prefix.removesuffix(":")
            key = f"{prefix}:{key}"
        if suffix is not None:
            suffix = suffix.removeprefix(":")
            key = f"{key}:{suffix}"
        return key


class BaseCache(ABC):
    """Базовый класс для реализации асинхронного кэша."""

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Получение данных из кэша по заданному ключу."""

    @abstractmethod
    async def set(
        self, key: str, data: Any, *, ttl: seconds | datetime.timedelta | None = None, create_missing: bool = True,
    ) -> bool:
        """Сохранение данных с заданным ключом и параметрами.

        Args:
            key: ключ, по которому надо сохранять данные.
            data: данные для сохранения.
            ttl: значение ttl (время жизни) ключа, в секундах или datetime.timedelta.
            create_missing: добавлять/обновлять запись с уже существующим ключом или нет.

        Returns:
            Были ли сохранены данные.
        """

    def get_ttl(self, ttl: seconds | datetime.timedelta | None = None) -> seconds | datetime.timedelta | None:
        """Получение `ttl` (таймаута) для записи в кэше."""
        if isinstance(ttl, datetime.timedelta):
            return ttl
        return None if ttl is None else max(0, int(ttl))


class BaseSyncCache(ABC):
    """Базовый класс для реализации синхронного кэша."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Получение данных из кэша по заданному ключу."""

    @abstractmethod
    def set(
        self, key: str, data: Any, *, ttl: seconds | datetime.timedelta | None = None, create_missing: bool = True,
    ) -> bool:
        """Сохранение данных с заданным ключом и параметрами.

        Args:
            key: ключ, по которому надо сохранять данные.
            data: данные для сохранения.
            ttl: значение ttl (время жизни) ключа, в секундах или datetime.timedelta.
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
    """Асинхронный кэш с использованием Redis."""

    def __init__(self, redis_client: RedisClient) -> None:
        assert isinstance(redis_client, RedisClient)
        self._redis_client = redis_client

    async def get(self, key: str, /, *, default: Any | None = None) -> Any:
        return await self._redis_client.get(key, default=default)

    async def set(
        self, key: str, data: Any, *, ttl: seconds | datetime.timedelta | None = None, create_missing: bool = True,
    ) -> bool:
        return await self._redis_client.set(key, data, timeout=self.get_ttl(ttl), create_missing=create_missing)


class SyncRedisCache(BaseSyncCache):
    """Синхронный кэш с использованием Redis."""

    def __init__(self, redis_client: SyncRedisClient) -> None:
        assert isinstance(redis_client, SyncRedisClient)
        self._redis_client = redis_client

    def get(self, key: str, /, *, default: Any | None = None) -> Any:
        return self._redis_client.get(key, default=default)

    def set(
        self, key: str, data: Any, *, ttl: seconds | datetime.timedelta | None = None, create_missing: bool = True,
    ) -> bool:
        return self._redis_client.set(key, data, timeout=self.get_ttl(ttl), create_missing=create_missing)
