from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from notifications.core.config import get_settings
from notifications.core.logging import configure_logger
from notifications.domain import messages, periodic_tasks, templates
from notifications.domain.factories import base_key_factory
from notifications.infrastructure.db import cache, postgres, redis, repositories
from notifications.infrastructure.db.cache import CacheKeyBuilder
from notifications.infrastructure.emails.clients import ConsoleClient
from notifications.infrastructure.emails.stubs import StreamStub
from notifications.integrations.auth.stubs import NetflixAuthClientStub
from notifications.integrations.ugc.stubs import NetflixUgcClientStub

from .helpers import sentinel

if TYPE_CHECKING:
    from celery import Celery

settings = get_settings()


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "notifications.celery",
            "notifications.api.v1.handlers.m2m",
            "notifications.api.v1.handlers.templates",
            "notifications.api.v1.handlers.dashboard",
            "notifications.domain.messages.tasks",
            "notifications.domain.periodic_tasks.tasks",
        ],
    )

    config = providers.Configuration(pydantic_settings=[settings])

    logging = providers.Resource(configure_logger)

    # Infrastructure

    db = providers.Singleton(
        postgres.AsyncDatabase,
        db_url=config.DB_URL,
    )

    redis_connection = providers.Resource(
        redis.init_redis,
        url=config.REDIS_URL,
    )

    redis_client = providers.Singleton(
        redis.RedisClient,
        redis_client=redis_connection,
    )

    cache_client = providers.Singleton(
        cache.RedisCache,
        redis_client=redis_client,
    )

    sync_redis_connection = providers.Resource(
        redis.init_sync_redis,
        url=config.REDIS_CELERY_URL,
    )

    sync_redis_client = providers.Singleton(
        redis.SyncRedisClient,
        redis_client=sync_redis_connection,
    )

    sync_cache_client = providers.Singleton(
        cache.SyncRedisCache,
        redis_client=sync_redis_client,
    )

    redis_repository_factory = providers.Factory(
        providers.Factory,
        repositories.RedisRepository,
    )

    email_client = providers.Singleton(
        ConsoleClient,
        stream=providers.Object(sys.stdout),
    )

    # Integrations -> Netflix Auth

    auth_client = providers.Singleton(
        # TODO [Дипломный проект]: После реализации всех клиентов АПИ тут будет использоваться настоящий клиент
        NetflixAuthClientStub,
    )

    # Integrations -> Netflix UGC

    ugc_client = providers.Singleton(
        # TODO [Дипломный проект]: После реализации всех клиентов АПИ тут будет использоваться настоящий клиент
        NetflixUgcClientStub,
    )

    # Domain -> Common

    cache_key_builder = providers.Singleton(CacheKeyBuilder)
    base_key_factory_ = providers.Callable(
        base_key_factory,
        key_builder=cache_key_builder,
        min_length=config.CACHE_HASHED_KEY_LENGTH,
    )

    # Domain -> Templates

    template_repository = providers.Singleton(
        templates.TemplateRepository,
        redis_repository=redis_repository_factory(model=templates.Template),
    )

    template_service = providers.Singleton(
        templates.TemplateService,
        template_repository=template_repository,
    )

    # Domain -> Messages

    email_notification_service = providers.Singleton(
        messages.EmailNotificationService,
        email_client=email_client,
        template_service=template_service,
        key_factory=base_key_factory_.provider,
        cache_client=cache_client,
    )

    notification_dispatcher_service = providers.Singleton(
        messages.NotificationDispatcherService,
        email_service=email_notification_service,
        template_service=template_service,
    )

    # Domain -> Periodic Tasks

    task_repository = providers.Factory(
        periodic_tasks.TaskRepository,
        celery_app=sentinel,
        session_factory=db.provided.session,
    )

    task_service = providers.Factory(
        periodic_tasks.TaskService,
        task_repository=task_repository,
        email_service=email_notification_service,
        template_service=template_service,
        auth_client=auth_client,
        ugc_client=ugc_client,
        key_factory=base_key_factory_.provider,
        cache_client=cache_client,
    )


def override_providers(container: Container) -> Container:
    """Перезаписывание провайдеров с помощью стабов."""
    if not container.config.USE_STUBS():
        return container
    container.email_client.override(providers.Singleton(ConsoleClient, stream=StreamStub))
    container.auth_client.override(providers.Singleton(NetflixAuthClientStub))
    container.ugc_client.override(providers.Singleton(NetflixUgcClientStub))
    return container


def inject_celery_app(container: Container, celery_app: Celery) -> Container:
    container.task_repository.add_kwargs(celery_app=celery_app)
    return container


async def dummy_resource() -> None:
    """Функция-ресурс для перезаписи в DI контейнере."""
