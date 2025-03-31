# schemas/person_schem.py
"""
Схемы для людей
"""
from pydantic import BaseModel, UUID4, EmailStr
from typing import Optional
from datetime import date


class PersonBase(BaseModel):
    name: str
    patronymic: Optional[str] = None
    surname: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    counterparty_id: Optional[int] = None
    birth_date: Optional[date] = None
    active: bool = True
    note: Optional[str] = None
    can_be_scheme_developer: bool = False
    can_be_assembler: bool = False
    can_be_programmer: bool = False
    can_be_tester: bool = False


class PersonResponse(PersonBase):
    uuid: UUID4

    class Config:
        """
        Конфигурация модели
        """
        from_attributes = True


class PersonCanBe(BaseModel):
    uuid: UUID4
    name: str
    patronymic: Optional[str] = None
    surname: str
    active: bool = True
    can_be_scheme_developer: bool = False
    can_be_assembler: bool = False
    can_be_programmer: bool = False
    can_be_tester: bool = False
    class Config:
        """
        Конфигурация модели
        """
        from_attributes = True