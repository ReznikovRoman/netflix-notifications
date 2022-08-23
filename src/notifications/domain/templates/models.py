from aredis_om import Field

from notifications.domain.models import BaseHashModel


class Template(BaseHashModel):
    """Шаблон уведомления."""

    name: str
    slug: str = Field(index=True)
    content: str
