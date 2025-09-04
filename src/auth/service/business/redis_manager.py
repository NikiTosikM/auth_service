from uuid import UUID
import json

from redis.asyncio import Redis

from core import settings


class RedisManager:
    """
    Добавление refresh_token при успешной аутентификации,
    а так же поиск и проверка токена на существование
    """

    def __init__(self, client: Redis):
        self._client = client

    async def adding_refresh_token(self, jti: str, user_id: UUID) -> None:
        """
        Добавляем refresh-token в redis
        применение: /login
        """
        token_data = {"user_id": str(user_id), "jti": jti}
        async with self._client.pipeline() as pipline:
            await pipline.set(f"refresh-token:{jti}", json.dumps(token_data))
            await pipline.expire(
                f"refresh-token:{jti}",
                settings.auth.refresh_token_lifetime_minutes,
            )
            await pipline.execute()

    async def expanding_list_invalid_tokens(self, jti: str) -> None:
        """
        Удаление refresh токена из списка допустимых
        применение: /logout  
        """
        await self._client.delete(f"refresh-token:{jti}")

    async def validation_token(self, jti: str) -> bool:
        """
        Проверяем валидность токена
        применение: /refresh   
        """
        existence_token: bool = await self._client.exists(f"refresh-token:{jti}")
        return existence_token
        
        