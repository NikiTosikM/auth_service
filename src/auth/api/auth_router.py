from typing import Annotated

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.api.dependencies import (
    get_current_user,
    get_jwt_token_depen,
    get_redis_client_depen,
    get_session_depen,
)
from src.auth.schemas import (
    JWTsPairSchema,
    UserLoginSchema,
    UserLogoutSchema,
    UserResponceSchema,
    UserSchema,
    UserEmailSchema,
)
from src.auth.service import UserAuthService
from src.auth.service.business.redis_manager import RedisManager
from src.auth.utils.jwt.jwt_manager import JwtToken
from src.tasks.tasks import send_email_message_to_user
from src.logger.config import log_endpoint


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    summary="Регистрация пользователя",
    response_model=UserResponceSchema,
    response_class=ORJSONResponse,
)
@log_endpoint
async def register_user(
    user: UserSchema,
    session: AsyncSession = Depends(get_session_depen),
):
    # регистрация пользователя
    user_service = UserAuthService(session=session)
    created_user: UserResponceSchema = await user_service.create_user(user_data=user)

    # отправка email message
    user_data_for_email_message = UserEmailSchema(
        name=user.name, last_name=user.last_name, recipient_email=user.email
    )
    send_email_message_to_user.delay(user_data=user_data_for_email_message.model_dump())

    return created_user


@router.post(
    "/login",
    response_model=JWTsPairSchema,
    response_class=ORJSONResponse,
    summary="Аутентификация и авторизация пользователя",
    description="Пользователь вводит свой пароль и почту и происходит проверка подлинности данных, \
    если все успешно, то выдается access и refresh токены",
)
@log_endpoint
async def login(
    auth_data: UserLoginSchema,
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
@log_endpoint
async def logout(
    logout_data: Annotated[UserLogoutSchema, Body()],
    credentials: HTTPAuthorizationCredentials = Depends(get_current_user),
    jwt: JwtToken = Depends(get_jwt_token_depen),
    redis: RedisManager = Depends(get_redis_client_depen),
):
    availability_refresh_token: UserResponceSchema = await redis.validation_token(
        jti=logout_data.refresh_token
    )
    jwt.validate_refresh_token(user_data=availability_refresh_token.id, token=jwt)
    await redis.expanding_list_invalid_tokens(jti=logout_data.refresh_token)

    return {"status": "success"}


@router.get(
    "/protected",
    summary="Защищенный метод",
    description="Обращение к данному методу без авторизации невозможно, \
        поэтому данный метод проверяет права пользователя и выдает доступ к данным",
)
@log_endpoint
def protected(
    credentials: HTTPAuthorizationCredentials = Depends(get_current_user),
) -> dict:
    return {"status": "success"}
