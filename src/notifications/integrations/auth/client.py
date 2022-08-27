from typing import Iterator

from .enums import DefaultRoles
from .types import BoundaryRegistrationDate, UserDetail


class NetflixAuthClient:
    """Клиент для работы с АПИ сервиса NetflixAuth."""

    # TODO [Дипломный проект]: сделать клиенты ко всем микросервисам и выложить в (закрытый) PyPI репозиторий
    # TODO [Дипломный проект]: добавить репозитории к integrations.auth

    def get_boundary_registration_dates(self, *, user_role: DefaultRoles | None = None) -> BoundaryRegistrationDate:
        """Получение граничных дат - дат регистрации первого и последнего пользователей.

        Используется для создания date-based чанков в периодических задачах.
        """

    def get_users_within_registration_date_range_iter(
        self, date_range: BoundaryRegistrationDate, /,
    ) -> Iterator[UserDetail]:
        """Получение данных пользователей по заданному диапазону дат регистрации.

        Возвращает итератор по пользователям.
        """

    def get_users_within_registration_date_range(self, date_range: BoundaryRegistrationDate, /) -> list[UserDetail]:
        """Получение данных пользователей по заданному диапазону дат регистрации."""
        return list(self.get_users_within_registration_date_range_iter(date_range))
