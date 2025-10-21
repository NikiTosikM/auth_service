from uuid import UUID

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status, Request

from core.db import db_core
from core import settings
from core.redis import redis_core
from auth.service import RedisManager
from auth.utils.jwt.jwt_manager import JwtToken
from auth.schemas import JWTPayloadSchema
from loguru import logger


security: HTTPAuthorizationCredentials = HTTPBearer()


async def get_session_depen():
    async with db_core.get_async_session() as session:
        yield session


async def get_redis_client_depen(request: Request):
    async with redis_core.create_client() as client:
        yield RedisManager(client=client)


async def get_jwt_token_depen():
    return JwtToken(
        private_key=settings.auth.private_key.read_text(),
        public_key=settings.auth.public_key.read_text(),
        algorithm=settings.auth.algorithm,
        access_token_lifetime_minutes=settings.auth.access_token_lifetime_minutes,
        refresh_token_lifetime_minutes=settings.auth.refresh_token_lifetime_minutes,
    )


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
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough rights", "detail": "You need to login"},
        )

    logger.debug("Проверка прав пользователя успешна")

    return user
