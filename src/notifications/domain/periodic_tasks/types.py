import uuid
from typing import TypedDict

from cron_validator import CronValidator
from pydantic import BaseModel, Field, root_validator

from notifications.core.config import get_settings

settings = get_settings()


class CeleryTask(BaseModel):
    """Celery задача."""

    name: str


class TaskCrontabSchedule(BaseModel):
    """Расписание периодической задачи."""

    minute: str | None = "*"
    hour: str | None = "*"
    day_of_week: str | None = "*"
    day_of_month: str | None = "*"
    month_of_year: str | None = "*"
    timezone: str | None = settings.celery.TIMEZONE

    @root_validator
    def check_cron_valid(cls, values):
        cron = cls.to_cron_from_values(values)
        if CronValidator.parse(cron) is None:
            raise ValueError(f"Given cron <{cron}> is not valid.")
        return values

    def to_cron(self) -> str:
        return f"{self.minute} {self.hour} {self.day_of_week} {self.day_of_month} {self.month_of_year}"

    @staticmethod
    def to_cron_from_values(values: dict, /) -> str:
        cron = (
            f"{values['minute']} {values['hour']} {values['day_of_week']} "
            f"{values['day_of_month']} {values['month_of_year']}"
        )
        return cron


class CeleryPeriodicTask(BaseModel):
    """Периодическая Celery задача."""

    task: str
    name: str
    description: str
    crontab: TaskCrontabSchedule
    kwargs: dict | None = Field(default_factory=dict)
    one_off: bool | None = False

    @root_validator
    def check_required_kwargs(cls, values):
        kwargs = values["kwargs"]
        if "template_slug" not in kwargs:
            raise ValueError("Template slug `template_slug` is missing in kwargs.")
        if "email_subject" not in kwargs:
            raise ValueError("Email subject `email_subject` is missing in kwargs.")
        return values


class UserPayload(TypedDict):
    """Сериализованные данные пользователя."""

    pk: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: str
    registration_date: str
