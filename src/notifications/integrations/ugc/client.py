import uuid
from typing import Iterator

from .types import RecommendationShortDetail


class NetflixUgcClient:
    """Клиент для работы с АПИ сервиса Netflix UGC."""

    # TODO [Дипломный проект]: сделать клиенты ко всем микросервисам и выложить в (закрытый) PyPI репозиторий
    # TODO [Дипломный проект]: добавить репозитории к integrations.ugc

    def get_recommendations_for_user_iter(self, user_pk: uuid.UUID, /) -> Iterator[RecommendationShortDetail]:
        """Получение рекомендаций для пользователя `user_pk`.

        Возвращает итератор.
        """

    def get_recommendations_for_user(self, user_pk: uuid.UUID, /) -> list[RecommendationShortDetail]:
        """Получение рекомендаций для пользователя `user_pk`."""
        return list(self.get_recommendations_for_user_iter(user_pk))
