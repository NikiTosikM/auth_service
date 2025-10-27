from uuid import UUID

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status

from src.core.db import db_core
from src.core.redis import redis_core
from src.auth.service import RedisManager
from src.auth.utils.jwt.jwt_manager import JwtToken
from src.auth.schemas import JWTPayloadSchema
from loguru import logger


security: HTTPAuthorizationCredentials = HTTPBearer()


async def get_session_depen():
    async with db_core.get_async_session() as session:
        yield session


async def get_redis_client_depen():
    async with redis_core.create_client() as client:
        yield RedisManager(client=client)


async def get_jwt_token_depen():
    return JwtToken()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_token: JwtToken = Depends(get_jwt_token_depen),
):
    logger.debug("Проверка прав пользователя")

    token: str = credentials.credentials
    payload: JWTPayloadSchema = jwt_token.decode_jwt_token(token)
    user: UUID = payload.sub
    role: str = payload.role

    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Not enough rights", "detail": "You need to login"},
        )

    logger.debug("Проверка прав пользователя успешна")

    return user
