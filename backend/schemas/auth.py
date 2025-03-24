# schemas/auth.py
from pydantic import BaseModel
from typing import Optional


# Схемы для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
