import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from notifications.core.config import get_settings

from .containers import Container, override_providers

settings = get_settings()


def create_app() -> FastAPI:
    container = Container()
    container.config.from_pydantic(settings=settings)
    container = override_providers(container)

    app = FastAPI(
        title="Netflix Notifications API v1",
        description="АПИ сервиса по работе с уведомлениями.",
        servers=[
            {"url": server_host}
            for server_host in settings.SERVER_HOSTS
        ],
        docs_url=f"{settings.API_V1_STR}/docs",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        default_response_class=ORJSONResponse,
        debug=settings.DEBUG,
    )

    @app.on_event("startup")
    async def startup():
        await container.init_resources()
        container.check_dependencies()
        logging.info("Start server")

    @app.on_event("shutdown")
    async def shutdown():
        await container.shutdown_resources()
        logging.info("Cleanup resources")

    app.container = container
    return app
