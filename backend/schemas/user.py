# schemas/user.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(..., description="User email address")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class User(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    managed_projects: List[int] = []


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)  # все поля обязательны

    id: int
    username: str = Field(..., min_length=3, max_length=20)
    password: bytes
    # email: EmailStr | None = None
    email: str | None = None  # Используем str вместо EmailStr
    active: bool = True
