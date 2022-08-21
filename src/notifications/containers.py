import sys

from dependency_injector import containers, providers

from notifications.core.logging import configure_logger
from notifications.infrastructure.emails.clients import ConsoleClient
from notifications.infrastructure.emails.stubs import StreamStub


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration()

    config = providers.Configuration()

    logging = providers.Resource(configure_logger)

    # Infrastructure

    email_client = providers.Singleton(
        ConsoleClient,
        stream=sys.stdout,
    )


def override_providers(container: Container) -> Container:
    """Перезаписывание провайдеров с помощью стабов."""
    if not container.config.USE_STUBS():
        return container
    container.email_client.override(providers.Singleton(ConsoleClient, stream=StreamStub))
    return container


async def dummy_resource() -> None:
    """Функция-ресурс для перезаписи в DI контейнере."""
