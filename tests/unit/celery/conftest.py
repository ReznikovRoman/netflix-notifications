import pytest
import redis

from notifications.celery import Task
from notifications.core.config import Settings, get_settings

_settings = get_settings()


@pytest.fixture(scope="session")
def settings() -> Settings:
    return _settings


@pytest.fixture
def redis_client(settings) -> redis.Redis:
    return redis.Redis.from_url(settings.REDIS_CELERY_URL)


@pytest.fixture(autouse=True)
def _autoflush_cache(redis_client):
    try:
        yield
    finally:
        redis_client.flushdb()


@pytest.fixture(scope="session")
def celery_config():
    return {
        "task_always_eager": True,
    }


@pytest.fixture(scope="session")
def celery_parameters():
    return {
        "task_cls": Task,
    }
