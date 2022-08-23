import sys

from dependency_injector import containers, providers

from notifications.core.logging import configure_logger
from notifications.domain import templates
from notifications.infrastructure.db import redis, repositories
from notifications.infrastructure.emails.clients import ConsoleClient
from notifications.infrastructure.emails.stubs import StreamStub


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration()

    config = providers.Configuration()

    logging = providers.Resource(configure_logger)

    # Infrastructure

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

    # Domain -> Templates

    template_repository = providers.Singleton(
        templates.TemplateRepository,
        redis_repository=redis_repository_factory(model=templates.Template),
    )

    template_service = providers.Singleton(
        templates.TemplateService,
        template_repository=template_repository,
    )


def override_providers(container: Container) -> Container:
    """Перезаписывание провайдеров с помощью стабов."""
    if not container.config.USE_STUBS():
        return container
    container.email_client.override(providers.Singleton(ConsoleClient, stream=StreamStub))
    return container


async def dummy_resource() -> None:
    """Функция-ресурс для перезаписи в DI контейнере."""
