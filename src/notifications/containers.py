from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from notifications.core.logging import configure_logger
from notifications.domain import messages, periodic_tasks, templates
from notifications.infrastructure.db import postgres, redis, repositories
from notifications.infrastructure.emails.clients import ConsoleClient
from notifications.infrastructure.emails.stubs import StreamStub
from notifications.integrations.auth.stubs import NetflixAuthClientStub
from notifications.integrations.ugc.stubs import NetflixUgcClientStub

from .helpers import sentinel

if TYPE_CHECKING:
    from celery import Celery


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "notifications.api.v1.handlers.m2m",
            "notifications.api.v1.handlers.templates",
            "notifications.api.v1.handlers.dashboard",
            "notifications.domain.messages.tasks",
            "notifications.domain.periodic_tasks.tasks",
        ],
    )

    config = providers.Configuration()

    logging = providers.Resource(configure_logger)

    # Infrastructure

    db = providers.Singleton(
        postgres.AsyncDatabase,
        db_url=config.DB_URL,
    )

    redis_client = providers.Resource(
        redis.init_redis,
        url=config.REDIS_OM_URL,
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
