from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, TimeoutError, SQLAlchemyError
from loguru import logger

from src.core import settings
from src.auth.exception.exception import OperationDBException, DBException, LongRequestTimeExecution


class DBCore:
    def __init__(self, url: str):
        self._async_engine = create_async_engine(
            url=url,
            echo=True,
        )
        self._async_sessionmaker: async_sessionmaker = async_sessionmaker(
            self._async_engine
        )

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._async_sessionmaker()
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            logger.error("Произошла непредвиденная ошибка sqlalchemy")
            await session.rollback()
            raise DBException
        finally:
            await session.close()
            
    async def test_request(self) -> None:
        try:
            logger.debug("Проверяется подключение к бд")
            async with self.get_async_session() as async_session:
                await async_session.execute(text("SELECT VERSION()"))
            logger.debug("Тестовое подключение к бд выполненно успешно")
        except TimeoutError:
            logger.error("Время обработки запроса превысило лимит")
            raise LongRequestTimeExecution
        except OperationalError:
            logger.error("Данный запрос не может быть обработан")
            raise OperationDBException
        except SQLAlchemyError:
            logger.error("Произошла непредвиденная ошибка sqlalchemy")
            raise DBException
            


db_core = DBCore(url=settings.db.get_db_url)
