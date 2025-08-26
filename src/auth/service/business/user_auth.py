from auth.exception import UserAlreadeRegistered
from auth.models.user import User
from auth.schemas import UserResponce, UserSchema
from auth.service.repository.user_data import UserRepository
from auth.utils.hash_password.hashing import hashing_password


class UserAuthService:
    def __init__(self, session):
        self._repository = UserRepository(session=session)

    async def create_user(self, user_data: UserSchema) -> UserResponce:
        await self._check_user_availability(user_email=user_data.email)
        hash_password: bytes = hashing_password.create_hash(user_data.password)
        user_data = {
            "name": user_data.name,
            "last_name": user_data.last_name,
            "email": user_data.email,
            "password": hash_password,
            "role": user_data.role
        }
        created_user: User = await self._repository.create_user(
            data=user_data
        )
        returning_user_data = UserResponce(**created_user.__dict__)

        return returning_user_data

    async def _check_user_availability(self, user_email: str) -> None:
        user: User | None = await self._get_user_by_email(user_email=user_email)
        if user:
            raise UserAlreadeRegistered(email=user_email)

    async def _get_user_by_email(self, user_email: str) -> User | None:
        user: User = await self._repository.user_search(email=user_email)
        return user
