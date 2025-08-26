from enum import Enum
from uuid import UUID
import re

from pydantic import (
    BaseModel, 
    Field, 
    EmailStr, 
    model_validator, 
    ValidationError
)


class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    
    
class UserSchema(BaseModel):
    name: str = Field(max_length=100, min_length=5)
    last_name: str = Field(max_length=150, min_length=5)
    email: EmailStr = Field(max_length=150, min_length=3)
    password: str = Field(min_length=12)
    role: UserRole
    
    @model_validator(mode="after")
    def validate_password(data: "UserSchema"):
        verif_expression = re.compile(r'^.*(?=.{8,})(?=.*[a-zA-Z])(?=.*\d)(?=.*[!#$%&? "]).*$')
        if not verif_expression.match(data.password):
            raise ValidationError("The password was not verified")
        return data
        

class UserResponce(BaseModel):
    id: UUID
    name: str
    last_name: str
    email: EmailStr
