import datetime
from typing import Iterator

from pydantic_factories import ModelFactory

from notifications.helpers import TZ_MOSCOW

from .client import NetflixAuthClient
from .enums import DefaultRoles
from .types import BoundaryRegistrationDate, UserDetail

model_factory = ModelFactory()

ALL_USERS: list[UserDetail] = model_factory.create_factory(UserDetail).batch(size=10)


class NetflixAuthClientStub(NetflixAuthClient):
    """Стаб клиента для работы с АПИ сервиса NetflixAuth."""

    def get_boundary_registration_dates(self, *, user_role: DefaultRoles | None = None) -> BoundaryRegistrationDate:
        return BoundaryRegistrationDate(
            first_registration_date=datetime.datetime.min.date(),
            last_registration_date=datetime.datetime.now(TZ_MOSCOW).date(),
        )

    def get_users_within_registration_date_range_iter(
        self, date_range: BoundaryRegistrationDate, /,
    ) -> Iterator[UserDetail]:
        for user in ALL_USERS:
            if date_range.first_registration_date <= user.registration_date < date_range.last_registration_date:
                yield user
