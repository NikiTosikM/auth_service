from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from auth.models.user import User
from auth.schemas import UserSchema
from auth.service.repository.base_repository import BaseRepository
from loguru import logger


class UserRepository(BaseRepository[User, UserSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=User)

    async def user_search(self, email) -> User | None:
        logger.debug(f"Поиск пользователь в БД по email - {email}")

        query = select(User).where(User.email == email)
        result: Result = await self.session.execute(query)

        logger.debug(f"Поиск  пользователь по email - {email} выполнен")

        return result.scalar_one_or_none()
