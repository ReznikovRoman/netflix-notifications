from typing import AsyncIterator

import aioredis
from aredis_om import Migrator


async def init_redis(url: str) -> AsyncIterator[aioredis.Redis]:
    redis_client: aioredis.Redis = await aioredis.from_url(url)
    await Migrator().run()
    yield redis_client
    await redis_client.close()
