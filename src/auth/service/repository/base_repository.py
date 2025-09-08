from uuid import UUID
from typing import TypeVar, Generic

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, Result, delete
from pydantic import BaseModel

from core.db import Base
from auth.models.user import User


Model = TypeVar("Model", bound=Base)
Schema = TypeVar("Schema", bound=BaseModel)


class BaseRepository(Generic[Model, Schema]):
    def __init__(
        self,
        model: type[Model],
        schema: type[Schema], 
        session: AsyncSession
    ):
        self.model = model
        self.schema = schema
        self.session = session
        
    async def create(self, data: Schema) -> Model:
        ''' Создание '''
        stmt = (
            insert(self.model)
            .values(data.model_dump())
            .returning(self.model)
        )
        result: Result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    
    async def delete_user(self, id: UUID) -> None:
        ''' Удаление '''
        stmt = delete(self.model).where(self.model.id == id)
        await self._session.execute(stmt)
