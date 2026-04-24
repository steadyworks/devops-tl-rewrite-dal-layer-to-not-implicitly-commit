import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.lib.utils.common import none_throws


class AsyncSessionFactory:
    def __init__(self) -> None:
        self._engine: AsyncEngine = create_async_engine(
            none_throws(os.getenv("SUPABASE_POSTGRES_URI")), echo=False, future=True
        )
        self._sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def context(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._sessionmaker() as session:
            try:
                yield session
            finally:
                await session.close()

    def get_dependency(self) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
        async def _get_session() -> AsyncGenerator[AsyncSession, None]:
            async with self.context() as session:
                yield session

        return _get_session

    def engine(self) -> AsyncEngine:
        return self._engine
