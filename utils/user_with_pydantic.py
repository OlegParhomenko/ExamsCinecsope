from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


class Roles(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class RegisteredUser(BaseModel):
    email: str
    fullName: str
    password: str = Field(..., min_length=8)
    passwordRepeat: str
    roles: List[Roles]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator('email')
    def check_email(cls, value):
        """
            Проверяем, есть ли @ в поле email
        """
        if '@' not in value:
            raise ValueError("@ знака нет в поле email")
        return value
