from uuid import UUID

from pydantic import BaseModel

from auth.schemas import UserRoleSchema


class JWTPayloadSchema(BaseModel):
    iss: str
    sub: UUID
    email: str
    role: UserRoleSchema
    exp: int
    jti: UUID
    
    
class JWTsLoginSchema(BaseModel):
    access_token: str
    refresh_token: str