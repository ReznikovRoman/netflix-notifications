import dataclasses
from typing import Protocol, Sequence

seconds = int


class _ModelMeta(type):
    """Мета-класс для создания датаклассов."""

    _dataclass_options = {
        "init": True,
        "repr": True,
        "eq": True,
        "order": True,
        "unsafe_hash": True,
        "frozen": True,
        "kw_only": True,
        "match_args": True,
        "slots": True,
    }
    _convert_to_dataclass = dataclasses.dataclass(**_dataclass_options)

    def __new__(cls, name, bases, namespace):  # noqa: N805
        obj = super().__new__(cls, name, bases, namespace)
        if "__slots__" in namespace:
            # Пересоздание класса внутри dataclasses.dataclass
            return obj
        return cls._convert_to_dataclass(obj)


class BaseModel(metaclass=_ModelMeta):
    """Базовый класс модели для тех сущностей, у которых нет поля `id`."""


class INotification(Protocol):
    """Уведомление."""

    subject: str
    content: str
    recipient_list: Sequence[str]
