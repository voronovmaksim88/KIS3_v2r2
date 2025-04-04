# schemas/order_schem.py
"""
Схемы для заказов
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from typing import List
from datetime import datetime
from pydantic import ConfigDict
from schemas.work_schem import WorkSchema


class OrderStatusSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        """
        Конфигурация модели
        """
        from_attributes = True


class CounterpartySchema(BaseModel):
    id: int
    name: str
    note: Optional[str] = None

    class Config:
        """
        Конфигурация модели
        """
        from_attributes = True


class OrderBase(BaseModel):
    serial: str
    name: str
    customer_id: int
    priority: Optional[int] = None
    status_id: int
    start_moment: Optional[datetime] = None
    deadline_moment: Optional[datetime] = None
    end_moment: Optional[datetime] = None
    materials_cost: Optional[int] = None
    materials_paid: bool = False
    products_cost: Optional[int] = None
    products_paid: bool = False
    work_cost: Optional[int] = None
    work_paid: bool = False
    debt: Optional[int] = None
    debt_paid: bool = False

    @field_validator('priority')
    def validate_priority(cls, v):
        """
        проверка валидности приоритета
        """
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Priority must be between 1 and 10")
        return v

    @field_validator('status_id')
    def validate_status_id(cls, v):
        """
        проверка валидности статуса
        """
        if v < 1 or v > 8:
            raise ValueError("Status ID must be between 1 and 8")
        return v


class OrderSerial(BaseModel):
    serial: str


# Схема для одного заказа при чтении
class OrderRead(BaseModel):
    serial: str
    name: str
    customer: str  # Ожидаем строку
    priority: Optional[int] = None
    status_id: int
    start_moment: Optional[datetime] = None
    deadline_moment: Optional[datetime] = None
    end_moment: Optional[datetime] = None
    materials_cost: Optional[int] = None
    materials_paid: bool
    products_cost: Optional[int] = None
    products_paid: bool
    work_cost: Optional[int] = None
    work_paid: bool
    debt: Optional[int] = None
    debt_paid: bool
    works: List[WorkSchema] = []  # Список работ, по умолчанию пустой

    # Оставляем from_attributes, тк другие поля могут мапиться
    model_config = ConfigDict(from_attributes=True)

# Схема для ответа с пагинацией
class PaginatedOrderResponse(BaseModel):
    total: int
    limit: int
    skip: int
    data: List[OrderRead]

# class OrderCreate(OrderBase):
#     pass
#
#
# class OrderUpdate(BaseModel):
#     name: Optional[str] = None
#     customer_id: Optional[int] = None
#     priority: Optional[int] = None
#     status_id: Optional[int] = None
#     deadline_moment: Optional[datetime] = None
#     end_moment: Optional[datetime] = None
#     materials_cost: Optional[int] = None
#     materials_paid: Optional[bool] = None
#     products_cost: Optional[int] = None
#     products_paid: Optional[bool] = None
#     work_cost: Optional[int] = None
#     work_paid: Optional[bool] = None
#     debt: Optional[int] = None
#     debt_paid: Optional[bool] = None
#
#     @validator('priority')
#     def validate_priority(cls, v):
#         if v is not None and (v < 1 or v > 10):
#             raise ValueError("Priority must be between 1 and 10")
#         return v
#
#     @validator('status_id')
#     def validate_status_id(cls, v):
#         if v is not None and (v < 1 or v > 8):
#             raise ValueError("Status ID must be between 1 and 8")
#         return v
#
#
# class OrderResponse(OrderBase):
#     customer: CounterpartySchema
#     status: OrderStatusSchema
#     works: List[WorkSchema] = []
#
#     class Config:
#         """
#         Конфигурация модели
#         """
#         from_attributes = True
#
#
# class OrderWithRelations(OrderResponse):
#     """Расширенная схема заказа со всеми связанными данными"""
#
#     class Config:
#         """
#         Конфигурация модели
#         """
#         from_attributes = True
#
#
# class OrderWorkAssociation(BaseModel):
#     order_serial: str
#     work_ids: List[int]
#
#     class Config:
#         """
#         Конфигурация модели
#         """
#         from_attributes = True
