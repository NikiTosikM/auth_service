from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import DataError
from fastapi import HTTPException, status

from auth.exception.exception import TokenValidException


class RedisManager:
    """
    Добавление refresh_token при успешной аутентификации,
    а так же поиск и проверка токена на нахождение в blacklist
    """

    def __init__(self, client: Redis):
        self._client = client

    async def adding_refresh_token(self, jti: str, user_id: UUID) -> None:
        """Добавляем refresh-token в redis"""
        await self._client.sadd(f"user:{user_id}:tokens", jti)
        # создаем обратную ссылку для проверки user_id в blacklist
        await self._client.set(f"token:{jti}:user", user_id)

    async def addendum_blacklist(self, jti: str, user_id: UUID) -> None:
        """Добавление токена в черный список"""
        try:
            true_token_owner: str = self._client.set(f"token:{jti}:users")
            if true_token_owner != str(user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid user_id is specified",
                )

            async with self._client.pipeline() as pipline:
                await pipline.srem(f"user:{user_id}:tokens", jti)
                await pipline.delete(f"token:{jti}:user", user_id)
                await pipline.sadd("blacklist:tokens", jti)
                await pipline.execute()
        except DataError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token is invalid"
            )

    async def is_token_valid(self, jti: str, user_id: UUID) -> bool:
        """Проверяем валидность токена"""
        token_active: bool = self._client.sismember(f"user:{user_id}:tokens", jti)
        if not token_active:
            raise TokenValidException("Token is not valid")
            
        find_token_in_blacklist = self._client.sismember("blacklist:tokens", jti)
        if find_token_in_blacklist:
            raise TokenValidException("Token is not valid")
        
        owned_by_user: bool = self._client.sismember(f"token:{jti}:user", user_id)
        if owned_by_user != str(user_id):
            raise TokenValidException("Token is not valid")
