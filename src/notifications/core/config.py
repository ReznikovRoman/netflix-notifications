from functools import lru_cache
from typing import Union

from kombu import Exchange, Queue
from pydantic import AnyHttpUrl, Field, validator
from pydantic.env_settings import BaseSettings


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class CelerySettings:
    """Настройки Celery."""

    CELERY_TIMEZONE = "Europe/Moscow"
    CELERY_ACCEPT_CONTENT = ["application/json"]
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TASK_SERIALIZER = "json"
    CELERY_TASK_RESULT_EXPIRES = 10 * 60
    CELERY_TASK_TIME_LIMIT = 8 * 60 * 60  # 8 hours
    CELERY_TASK_SOFT_TIME_LIMIT = 10 * 60 * 60  # 10 hours
    CELERY_QUEUES = (
        Queue(name="default", exchange=Exchange("default"), routing_key="default"),
        Queue(name="celery"),
        Queue(name="emails"),
        Queue(name="urgent_notifications"),
    )
    CELERY_CREATE_MISSING_QUEUES = True
    CELERY_DEFAULT_QUEUE = "default"
    CELERY_DEFAULT_EXCHANGE = "default"
    CELERY_DEFAULT_ROUTING_KEY = "default"


class Settings(BaseSettings):
    """Настройки проекта."""

    # Project
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str
    SERVER_HOSTS: Union[str, list[AnyHttpUrl]]
    PROJECT_NAME: str
    DEBUG: bool = Field(False)
    PROJECT_BASE_URL: str

    # Auth
    JWT_AUTH_SECRET_KEY: str = Field(env="NAA_SECRET_KEY")
    JWT_AUTH_ALGORITHM: str = "HS256"

    # Postgres
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_URL: str = None

    # Redis
    REDIS_DECODE_RESPONSES: bool = Field(True)
    REDIS_PORT: int = Field(6379)
    REDIS_URL: str
    REDIS_OM_URL: str
    REDIS_CELERY_URL: str = Field(..., env="NN_CELERY_BROKER_URL")
    REDIS_KEY_PREFIX: str = Field("notifications")

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    celery: CelerySettings = CelerySettings()

    class Config(EnvConfig):
        env_prefix = "NN_"
        case_sensitive = True

    @validator("SERVER_HOSTS", pre=True)
    def _assemble_server_hosts(cls, server_hosts):
        if isinstance(server_hosts, str):
            return [item.strip() for item in server_hosts.split(",")]
        return server_hosts

    @validator("DB_URL", pre=True)
    def get_db_url(cls, value, values) -> str:
        if value is not None:
            return value
        user = values["DB_USER"]
        password = values["DB_PASSWORD"]
        host = values["DB_HOST"]
        port = values["DB_PORT"]
        database = values["DB_NAME"]
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
