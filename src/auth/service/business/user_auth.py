from auth.exception import UserAlreadeRegistered, IncorrectUserLoginData
from auth.models.user import User
from auth.schemas import UserResponceSchema, UserSchema, UserLoginSchema, UserDBSchema
from auth.service.repository.user_repository import UserRepository
from auth.utils.hash_password.hashing import hashing


class UserAuthService:
    def __init__(self, session):
        self._user_repository = UserRepository(session=session)

    async def create_user(self, user_data: UserSchema) -> UserResponceSchema:
        """Создание пользователя"""
        await self._check_user_availability(user_email=user_data.email)

        hash_password: bytes = hashing.create_hash(user_data.password)
        user_data = UserDBSchema(
            name=user_data.name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=hash_password,
            role=user_data.role
        )

        created_user: User = await self._user_repository.create(data=user_data)
        returning_user_data = UserResponceSchema(**created_user.__dict__)

        return returning_user_data

    async def check_correctness_user_data(
        self, user_data: UserLoginSchema
    ) -> UserResponceSchema | None:
        """
        Проверка на существование пользователя по email
        Необходимо при входе в аккаунт. Если пользователч НЕТ, то выбрасываем исключение
        """
        user_presence: User | None = await self._get_user_by_email(
            user_email=user_data.login
        )
        password_matching: bool = hashing.hash_verification(
            data=user_data.password, hash=user_presence.password
        ) if user_presence else False
        if not user_presence or not password_matching:
            raise IncorrectUserLoginData(
                password=user_data.password, login=user_data.login
            )

        return UserResponceSchema(**user_presence.__dict__)

    async def _check_user_availability(self, user_email: str) -> User | None:
        """
        Поиск пользователя по email
        Необходимо при регистрации пользователя. Если он СУЩЕСТВУЕТ, то вызываем ошибку
        """
        user: User | None = await self._get_user_by_email(user_email=user_email)
        if user:
            raise UserAlreadeRegistered(email=user_email)
        return user

    async def _get_user_by_email(self, user_email: str) -> User | None:
        """Поиск пользователя по email"""
        user: User | None = await self._user_repository.user_search(email=user_email)
        return user
