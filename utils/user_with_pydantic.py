from pydantic import BaseModel
from typing import List

class RegisteredUser(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: List[str]
