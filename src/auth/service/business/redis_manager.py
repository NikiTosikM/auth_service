import json

from redis.asyncio import Redis
from loguru import logger

from src.core import settings
from src.auth.schemas import UserResponceSchema


class RedisManager:
    """
    Добавление refresh_token при успешной аутентификации,
    а так же поиск и проверка токена на существование
    """

    def __init__(self, client: Redis):
        self._client = client

    async def adding_refresh_token(
        self, jti: str, user_data: UserResponceSchema
    ) -> None:
        """
        Добавляем refresh-token в redis
        применение: /login
        """
        token_data = {
            "id": str(user_data.id),
            "email": user_data.email,
            "role": user_data.role,
        }

        logger.debug(f"Добавление токена {jti} для пользователя {user_data.id}")

        async with self._client.pipeline() as pipline:
            await pipline.set(f"refresh-token:{jti}", json.dumps(token_data))
            await pipline.expire(
                f"refresh-token:{jti}",
                settings.auth.refresh_token_lifetime_minutes,
            )
            await pipline.execute()

        logger.debug(f"Токен {jti} добавлен")

    async def expanding_list_invalid_tokens(self, jti: str) -> None:
        """
        Удаление refresh токена из списка допустимых
        применение: /logout
        """
        logger.debug(f"Удаление токена  {jti} ")
        await self._client.delete(f"refresh-token:{jti}")
        logger.debug(f"Токена {jti} удален")

    async def validation_token(self, jti: str) -> UserResponceSchema | None:
        """
        Проверяем валидность токена. Если токен существует, то получаем данные о пользователе
        применение: /refresh
        """
        logger.debug(f"Поиск токена {jti}")
        serialized_data = await self._client.get(
            f"refresh-token:{jti}"
        )  # получаем данные по ключу
        if serialized_data:
            logger.debug(f"Токен {jti} найден")

            result: dict = json.loads(serialized_data)
            user_data: UserResponceSchema = UserResponceSchema(**result)
        else:
            logger.debug(f"Токен {jti} не найден")

        return user_data if serialized_data else None
