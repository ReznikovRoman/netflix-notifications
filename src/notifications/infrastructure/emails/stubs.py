class StreamStub:
    """Стаб потока для тестирования."""

    def write(self, message: str) -> None:
        print(message)

    def flush(self) -> None:
        ...
