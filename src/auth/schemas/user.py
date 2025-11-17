import re
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, ValidationInfo, field_validator

from src.auth.exception.exception import (
    UserEmailShortException,
    UserLastNameShortException,
    UserNameShortException,
    UserPasswordUncorrctedException,
)


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class UserSchema(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: str
    role: UserRole

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str):
        if len(name) < 5 or len(name) > 100:
            raise UserNameShortException
        
        return name

    @field_validator("last_name", "email")
    @classmethod
    def validate_last_name(cls, value: str, field: ValidationInfo):
        field_name: str = field.field_name

        if len(value) < 5 or len(value) > 150:
            if field_name == "last_name":
                raise UserLastNameShortException
            else:
                raise UserEmailShortException

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        verif_expression = re.compile(
            r'^.*(?=.{8,})(?=.*[a-zA-Z])(?=.*\d)(?=.*[!#$%&? "]).*$'
        )
        if not verif_expression.match(password):
            raise UserPasswordUncorrctedException
        
        return password


class UserDBSchema(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: bytes
    role: UserRole


class UserResponceSchema(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole


class UserLoginSchema(BaseModel):
    login: EmailStr
    password: str

class UserEmailSchema(BaseModel):
    name: str
    last_name: str
    recipient_email: str
