import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from auth.schemas import JWTPayloadSchema
from loguru import logger

from src.auth.schemas import UserResponceSchema
from src.core import settings
from src.auth.exception import TokenValidException
from src.auth.schemas import UserRole


class JwtToken:
    _private_key: str = settings.auth.private_key.read_text()
    _public_key: str = settings.auth.public_key.read_text()
    _algorithm: str = settings.auth.algorithm
    _access_token_lifetime_minutes: int = settings.auth.access_token_lifetime_minutes
    _refresh_token_lifetime_minutes: int = settings.auth.refresh_token_lifetime_minutes

    @classmethod
    def create_access_jwt_token(cls, user_id: UUID, email: str, role: UserRole) -> str:
        """
        Создание access-token
        применение: /login, /refresh
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=cls._access_token_lifetime_minutes
        )
        payload = {
            "iss": settings.app.host,
            "sub": str(user_id),
            "email": email,
            "role": role,
            "exp": expire,
            "jti": str(uuid4()),
        }

        logger.debug(f"Создание access_token с данными {payload}")

        return jwt.encode(
            payload=payload, key=cls._private_key, algorithm=cls._algorithm
        )

    @staticmethod
    def create_refresh_jwt_token() -> str:
        """
        Создание refresh-token
        применение: /login, /refresh
        """
        refresh_token: str = secrets.token_urlsafe(32)

        logger.debug(f"Создание refresh_token {refresh_token}")

        return refresh_token

    @classmethod
    def issuing_tokens(cls, user_data: UserResponceSchema) -> tuple[str, str]:
        """
        Создание refresh и access tokens
        применение: /login, /refresh
        """
        # создаем refresh token
        creation_ref_token: str = cls.create_refresh_jwt_token()
        # создаем access token
        creation_access_token: str = cls.create_access_jwt_token(
            user_id=user_data.id, email=user_data.email, role=user_data.role
        )
        logger.debug("Access и refresh токены созданы")
        return creation_access_token, creation_ref_token

    @classmethod
    def decode_jwt_token(cls, token: str) -> JWTPayloadSchema:
        try:
            decoded_payload = jwt.decode(token, cls._public_key, cls._algorithm)

            return JWTPayloadSchema(**decoded_payload)

        except jwt.InvalidSignatureError:
            logger.error(f"Token {token} signature is not valid")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token signature is invalid",
            )
        except jwt.ExpiredSignatureError:
            logger.error(f"Token {token} has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            logger.error(f"Token {token} is not valid")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid"
            )
        # обработать еще pydantic ошибки

    def validate_refresh_token(
        self, user_data: UserResponceSchema | None, token: str
    ) -> None:
        if not user_data:
            logger.error(f"Token {token} is not valid")
            raise TokenValidException("Token is not valid")
