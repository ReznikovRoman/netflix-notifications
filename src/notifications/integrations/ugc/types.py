import uuid

from pydantic import BaseModel


class RecommendationShortDetail(BaseModel):
    """Короткая информации о рекомендованном фильме."""

    pk: uuid.UUID
    title: str
    description: str
    photo: str
