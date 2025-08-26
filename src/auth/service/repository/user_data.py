from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, delete, select, Result, UUID

from auth.schemas import UserSchema
from auth.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_user(self, data: dict) -> User:
        query = (
            insert(User)
            .values(data)
            .returning(User)
        )
        result: Result = await self._session.execute(query)
        created_user: User = result.scalar_one_or_none()

        return created_user

    async def user_search(self, email) -> User | None:
        query = select(User).where(User.email == email)
        result: Result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def delete_user(self, user_id: UUID) -> None:
        query = delete(User).where(User.id == user_id)
        await self._session.execute(query)
