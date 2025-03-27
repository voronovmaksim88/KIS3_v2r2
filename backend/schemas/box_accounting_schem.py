#  schemas / box_accounting_schem.py
"""
Все схемы для учета шкафов
"""
from pydantic import BaseModel
from typing import Optional, List
import uuid


class PersonBase(BaseModel):
    uuid: uuid.UUID
    name: str
    surname: str
    patronymic: Optional[str]

    class Config:
        """
        Конфигурация модели
        """
        from_attributes = True


class BoxAccountingBase(BaseModel):
    serial_num: int
    name: str
    order_id: str


class BoxAccountingCreate(BaseModel):
    name: str
    order_id: str
    scheme_developer_id: uuid.UUID
    assembler_id: uuid.UUID
    programmer_id: Optional[uuid.UUID] = None
    tester_id: uuid.UUID


class BoxAccountingResponse(BoxAccountingBase):
    scheme_developer: PersonBase
    assembler: PersonBase
    programmer: Optional[PersonBase] = None
    tester: PersonBase

    class Config:
        """
        Конфигурация модели
        """
        from_attributes = True


class PaginatedBoxAccounting(BaseModel):
    """
    Модель для пагинированного ответа с данными учета шкафов.
    """
    items: List[BoxAccountingResponse]  # Список записей учета шкафов
    total: int  # Общее количество записей
    page: int  # Текущая страница
    size: int  # Количество элементов на странице
    pages: int  # Общее количество страниц

    class Config:
        """
        Конфигурация модели
        """
        from_attributes = True  # Разрешает работу с ORM-моделями
