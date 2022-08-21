from abc import ABC, abstractmethod
from typing import ClassVar, Protocol, Sequence

from notifications.helpers import BaseModel


class IStream(Protocol):
    """Интерфейс потока на запись."""

    def write(self, message: str, /) -> None:
        """Запись сообщения `message` в поток."""

    def flush(self) -> None:
        """Очистка потока."""


class EmailMessageDetail(BaseModel):
    """Информация о письме."""

    subject: str
    message: str
    recipient_list: Sequence[str]
    from_email: str | None = None

    def __str__(self) -> str:
        message_repr = (
            f"<Subject: {self.subject}>; <To: {self.recipient_list}>; <Message: {self.message}>\n"
        )
        return message_repr


class BaseEmailClient(ABC):
    """Базовый класс почтового клиента."""

    DEFAULT_FROM_EMAIL: ClassVar[str]

    @abstractmethod
    def send_messages(self, messages_details: Sequence[EmailMessageDetail], /) -> int:
        """Отправка одного или нескольких писем.

        Returns:
            Количество отправленных писем.
        """


class ConsoleClient(BaseEmailClient):
    """Тестовый клиент для 'отправки' писем в консоль."""

    DEFAULT_FROM_EMAIL = "dummy@local.com"

    def __init__(self, stream: IStream) -> None:
        self.stream = stream

    def send_messages(self, messages_details: Sequence[EmailMessageDetail], /) -> int:
        message_count = 0
        if not messages_details:
            return message_count
        for message_details in messages_details:
            self._write_message(message_details)
            message_count += 1
        return message_count

    def _write_message(self, email: EmailMessageDetail, /) -> None:
        self.stream.write(str(email))
        self.stream.flush()
