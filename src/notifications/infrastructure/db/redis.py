from typing import Any, AsyncIterator, Iterator

import aioredis
import redis
from aredis_om import Migrator

from notifications.types import seconds


async def init_redis(url: str) -> AsyncIterator[aioredis.Redis]:
    """Инициализация клиентов async Redis и Redis OM."""
    redis_client: aioredis.Redis = await aioredis.from_url(url)
    await Migrator().run()
    yield redis_client
    await redis_client.close()


def init_sync_redis(url: str) -> Iterator[redis.StrictRedis]:
    """Инициализация синхронного клиента Redis."""
    redis_client = redis.StrictRedis.from_url(url=url)
    yield redis_client
    redis_client.close()


class RedisClient:
    """Асинхронный клиент для работы с Redis."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        assert isinstance(redis_client, aioredis.Redis)
        self._redis_client = redis_client

    def get_client(self, key: str | None = None, *, write: bool = False) -> aioredis.Redis:
        return self._get_client(write)

    async def get(self, key: str, /, *, default: Any | None = None) -> Any:
        client = self.get_client()
        data = await client.get(key)
        return default if data is None else data

    async def set(self, key: str, data: Any, *, timeout: seconds | None = None, create_missing: bool = True) -> bool:
        client = self.get_client(write=True)
        options = {
            "ex": timeout,
            "nx": not create_missing,
        }
        return await client.set(key, data, **options)

    def _get_client(self, write: bool = False) -> aioredis.Redis:
        return self._redis_client


class SyncRedisClient:
    """Синхронный клиент для работы с Redis."""

    def __init__(self, redis_client: redis.StrictRedis) -> None:
        assert isinstance(redis_client, redis.StrictRedis)
        self._redis_client = redis_client

    def get_client(self, key: str | None = None, *, write: bool = False) -> redis.StrictRedis:
        return self._get_client(write)

    def get(self, key: str, /, *, default: Any | None = None) -> Any:
        client = self.get_client()
        data = client.get(key)
        return default if data is None else data

    def set(self, key: str, data: Any, *, timeout: seconds | None = None, create_missing: bool = True) -> bool:
        client = self.get_client(write=True)
        options = {
            "ex": timeout,
            "nx": not create_missing,
        }
        return client.set(key, data, **options)

    def _get_client(self, write: bool = False) -> redis.StrictRedis:
        return self._redis_client
