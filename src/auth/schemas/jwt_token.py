from uuid import UUID

from pydantic import BaseModel

from src.auth.schemas import UserRole


class JWTPayloadSchema(BaseModel):
    iss: str
    sub: UUID
    email: str
    role: UserRole
    exp: int
    jti: UUID


class JWTsPairSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str
