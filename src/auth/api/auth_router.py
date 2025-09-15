from typing import Annotated

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api.dependencies import (
    get_current_user,
    get_jwt_token_depen,
    get_redis_client_depen,
    get_session_depen,
)
from auth.schemas import (
    JWTsPairSchema,
    UserLoginSchema,
    UserLogoutSchema,
    UserResponceSchema,
    UserSchema,
)
from auth.service import UserAuthService
from auth.service.business.redis_manager import RedisManager
from auth.utils.jwt.jwt_manager import JwtToken


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    summary="Регистрация пользователя",
    response_model=UserResponceSchema,
    response_class=ORJSONResponse,
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
    response_model=JWTsPairSchema,
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
    await redis.adding_refresh_token(jti=refresh_token, user_data=user)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post(
    "/logout",
    summary="Выход пользователя из аккаунта",
    description="Удаляет refresh-token пользователя, \
    для того чтобы в дальнейшем нельзя было обновить access-token",
)
async def logout(
    logout_data: Annotated[UserLogoutSchema, Body()],
    credentials: HTTPAuthorizationCredentials = Depends(get_current_user),
    jwt: JwtToken = Depends(get_jwt_token_depen),
    redis: RedisManager = Depends(get_redis_client_depen),
):
    availability_refresh_token: UserResponceSchema = await redis.validation_token(
        jti=logout_data.refresh_token
    )
    jwt.validate_refresh_token(user_id=availability_refresh_token.id)
    await redis.expanding_list_invalid_tokens(jti=logout_data.refresh_token)

    return {"status": "success"}


@router.get(
    "/protected",
    summary="Защищенный метод",
    description="Обращение к данному методу без авторизации невозможно, \
        поэтому данный метод проверяет права пользователя и выдает доступ к данным",
)
def protected(credentials: HTTPAuthorizationCredentials = Depends(get_current_user)):
    return {"status": "success"}
