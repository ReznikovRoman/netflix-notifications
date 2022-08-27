import uuid
from typing import Iterator

from pydantic_factories import ModelFactory

from .client import NetflixUgcClient
from .types import RecommendationShortDetail

model_factory = ModelFactory()

PHOTO = (
    "https://occ-0-2794-2219.1.nflxso.net/dnm/api/v6/X194eJsgWBDE2aQbaNdmCXGUP-Y/"
    "AAAABbCZLCs9HAhpPgwyZ1nNNMDxaCYJKy92y48ZEzVgyQDuaPOCNIFaejGFHQyhMlyeMFUjNfXrElhWQQNdK74UAbUF2hNj.jpg?r=d4b"
)

RECOMMENDATIONS: list[RecommendationShortDetail] = (
    model_factory.create_factory(RecommendationShortDetail, photo=PHOTO).batch(size=2)
)


class NetflixUgcClientStub(NetflixUgcClient):
    """Стаб клиента для работы с АПИ сервиса Netflix UGC."""

    def get_recommendations_for_user_iter(self, user_pk: uuid.UUID, /) -> Iterator[RecommendationShortDetail]:
        for recommendation in RECOMMENDATIONS:
            yield recommendation
