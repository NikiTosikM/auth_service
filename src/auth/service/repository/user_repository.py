from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from auth.models.user import User
from auth.schemas import UserSchema
from auth.service.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=User)

    async def user_search(self, email) -> User | None:
        query = select(User).where(User.email == email)
        result: Result = await self.session.execute(query)

        return result.scalar_one_or_none()
