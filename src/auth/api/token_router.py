from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from auth.service.business.redis_manager import RedisManager
from auth.utils.jwt.jwt_manager import JwtToken
from auth.api.dependencies import get_redis_client_depen, get_jwt_token_depen
from auth.schemas import JWTsPairSchema, RefreshTokenSchema, UserResponceSchema


router = APIRouter(prefix="/token", tags=["Работа с токеном"])


@router.post(
    "/refresh",
    response_model=JWTsPairSchema,
    response_class=ORJSONResponse,
    summary="Обновление refresh и access токена",
    description="Данный метод будет получать refresh токен, \
        валидировать его и в последующем создаст новые access, refresh токены и отдаст их пользователь",
)
async def refresh_tokens(
    refresh_token: RefreshTokenSchema,
    redis: RedisManager = Depends(get_redis_client_depen),
    jwt: JwtToken = Depends(get_jwt_token_depen),
):
    # проверяем валидность refresh токена и получаем данные о пользователе, если он валиден
    user_data: UserResponceSchema | None = await redis.validation_token(
        jti=refresh_token.refresh_token
    )
    jwt.validate_refresh_token(user_data=user_data)

    # удаляем старый refresh токен из redis
    await redis.expanding_list_invalid_tokens(jti=refresh_token.refresh_token)

    # создаем новую пару refresh и access токенов
    access_token, refresh_token = jwt.issuing_tokens(user_data=user_data)

    # сохраняем созданный refresh токен в redis
    await redis.adding_refresh_token(jti=refresh_token, user_data=user_data)

    return {"access_token": access_token, "refresh_token": refresh_token}
