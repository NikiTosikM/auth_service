import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from auth.schemas import JWTPayloadSchema

from auth.schemas import UserResponceSchema
from core import settings
from auth.exception import TokenValidException



class JwtToken:
    def __init__(
        self, 
        private_key: str,
        public_key: str,
        algorithm: str,
        access_token_lifetime_minutes: int,
        refresh_token_lifetime_minutes: int
        ):
        self._private_key: str = private_key
        self._public_key: str = public_key
        self._access_token_lifetime: int = access_token_lifetime_minutes
        self._refresh_token_lifetime: int = refresh_token_lifetime_minutes
        self._algorithm: str = algorithm

    def create_access_jwt_token(self, user_data: UserResponceSchema) -> str:
        """
        Создание access-token
        применение: /login, /refresh
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_lifetime
        )
        payload = {
            "iss": settings.app.host,
            "sub": str(user_data.id),
            "email": user_data.email,
            "role": user_data.role,
            "exp": expire,
            "jti": str(uuid4()),
        }
        return jwt.encode(
            payload=payload, key=self._private_key, algorithm=self._algorithm
        )

    def create_refresh_jwt_token(self, user_id: UUID) -> str:
        """
        Создание refresh-token
        применение: /login, /refresh
        """
        refresh_token: str = secrets.token_urlsafe(32)
        return refresh_token

    def issuing_tokens(self, user_data: UserResponceSchema) -> tuple[str, str]:
        '''
        Выдача пользователю refresh и access tokens
        применение: /login, /refresh
        '''
        # создаем refresh token
        creation_ref_token: str = self.create_refresh_jwt_token(
            user_data.id
        )
        # создаем access token
        creation_access_token: str = self.create_access_jwt_token(
            user_data=user_data
        )
        return creation_access_token, creation_ref_token

    def decode_jwt_token(self, token: str) -> JWTPayloadSchema:
        try:
            decoded_payload = jwt.decode(token, self._public_key, self._algorithm)

            return JWTPayloadSchema(**decoded_payload)

        except jwt.InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token signature is invalid",
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid"
            )
        #обработать еще pydantic ошибки 
        
    def validate_refresh_token(self, token: str) -> None:
        if not token:
            raise TokenValidException("Token is not valid")
        
            
        