from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core import settings


class DBCore:
    def __init__(self, url: str):
        self._async_engine = create_async_engine(
            url=url,
            echo=True,
        )
        self._async_sessionmaker: async_sessionmaker = async_sessionmaker(self._async_engine)

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._async_sessionmaker() as session:
            yield session


db_core = DBCore(url=settings.db.get_db_url)
