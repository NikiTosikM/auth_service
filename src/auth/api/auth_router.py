from typing import Annotated

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserSchema, UserResponceSchema, UserLoginSchema, JWTsLoginSchema
from auth.api.dependencies import get_session_depen
from auth.service import UserAuthService
from auth.utils.jwt.jwt_manager import JwtToken
from auth.service.business.redis_manager import RedisManager
from auth.api.dependencies import get_redis_client_depen, get_jwt_token_depen

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    summary="Регистрация пользователя", 
    response_model=UserResponceSchema
)
async def register_user(
    user: Annotated[UserSchema, Body()],
    session: AsyncSession = Depends(get_session_depen),
):
    user_service = UserAuthService(session=session)

    created_user: UserResponceSchema = await user_service.create_user(user_data=user)

    return created_user


@router.post(
    "/login",
    response_model=JWTsLoginSchema, 
    response_class=ORJSONResponse,
    summary="Аутентификация и авторизация пользователя",
    description="Пользователь вводит свой пароль и почту и происходит проверка подлинности данных, \
    если все успешно, то выдается access и refresh токены",
)
async def login(
    auth_data: Annotated[UserLoginSchema, Body()],
    jwt: JwtToken = Depends(get_jwt_token_depen),
    session: AsyncSession = Depends(get_session_depen),
    redis: RedisManager = Depends(get_redis_client_depen),
):
    # поиск пользователя по email и проверка пароля
    user_service = UserAuthService(session=session)
    user: UserResponceSchema = await user_service.check_correctness_user_data(
        user_data=auth_data
    )

    # создание токенов
    access_token, refresh_token = jwt.issuing_tokens(user_data=user)
    # сохранение refresh токена в redis
    await redis.adding_refresh_token(jti=refresh_token, user_id=user.id)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/logout")
async def logout(
    jwt: JwtToken = Depends(get_jwt_token_depen),
    redis: RedisManager = Depends(get_redis_client_depen),
):
    pass
