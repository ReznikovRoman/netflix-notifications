import uuid

from pydantic import BaseModel


class RecommendationShortDetail(BaseModel):
    """Короткая информация о рекомендованном фильме."""

    pk: uuid.UUID
    title: str
    description: str
    photo: str
