from uuid import UUID
from typing import TypeVar, Generic

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, Result, delete
from pydantic import BaseModel

from core.db import Base
from loguru import logger


Model = TypeVar("Model", bound=Base)
Schema = TypeVar("Schema", bound=BaseModel)


class BaseRepository(Generic[Model, Schema]):
    def __init__(self, model: type[Model], schema: type[Schema], session: AsyncSession):
        self.model = model
        self.schema = schema
        self.session: AsyncSession = session

    async def create(self, data: Schema) -> Model:
        """Создание"""
        logger.debug(f"Starting create for {self.model.__name__} with data: {data}")

        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result: Result = await self.session.execute(stmt)

        logger.debug(
            f"Create the object model {self.model.__name__} completed. Data - {data}"
        )

        return result.scalar_one()

    async def delete_user(self, id: UUID) -> None:
        """Удаление"""
        logger.debug(f"Starting delete object {self.model.__name__} with id: {id}")

        stmt = delete(self.model).where(self.model.id == id)
        await self._session.execute(stmt)

        logger.debug(
            f"Deleted the object model {self.model.__name__} completed. ID - {id}"
        )
