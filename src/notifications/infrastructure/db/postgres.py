import logging
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Callable

from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class AsyncDatabase:
    """Абстракция над БД и SQLAlchemy."""

    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            ),
        )

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        """Контекстный менеджер для работы с сессией БД."""
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            logging.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
