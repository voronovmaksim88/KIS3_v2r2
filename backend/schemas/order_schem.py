# schemas/order_schem.py
"""
Схемы для заказов
"""

from pydantic import BaseModel, field_validator
from pydantic import Field
from typing import Optional
from typing import List
from pydantic import ConfigDict
from schemas.work_schem import WorkSchema
from datetime import datetime
from schemas.task_schem import TaskSchema
from schemas.timing_schem import TimingSchema


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
    def validate_priority(cls, v):  # noqa
        """
        проверка валидности приоритета
        """
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Priority must be between 1 and 10")
        return v

    @field_validator('status_id')
    def validate_status_id(cls, v):  # noqa
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


# Схема для комментария
class OrderCommentSchema(BaseModel):
    id: int
    moment_of_creation: Optional[datetime] = None
    text: str
    person: str  # Заменено person_uuid на person (строка с ФИО)

    class Config:
        from_attributes = True


# Схема для детального ответа
# Схема для детального ответа (ИЗМЕНЕННАЯ)
class OrderDetailResponse(OrderRead):
    comments: List[OrderCommentSchema] = []  # Указываем тип явно
    tasks: List[TaskSchema] = []  # Указываем тип явно
    timings: List[TimingSchema] = []  # Указываем тип явно


class OrderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="Название заказа")
    customer_id: int = Field(..., description="ID заказчика")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Приоритет от 1 до 10")
    status_id: int = Field(..., ge=1, le=8, description="ID статуса заказа")
    start_moment: Optional[datetime] = Field(None, description="Дата и время начала")
    deadline_moment: Optional[datetime] = Field(None, description="Дата и время дедлайна")
    end_moment: Optional[datetime] = Field(None, description="Дата и время завершения")
    materials_cost: Optional[int] = Field(None, description="Стоимость материалов")
    materials_paid: Optional[bool] = Field(False, description="Материалы оплачены")
    products_cost: Optional[int] = Field(None, description="Стоимость товаров")
    products_paid: Optional[bool] = Field(False, description="Товары оплачены")
    work_cost: Optional[int] = Field(None, description="Стоимость работ")
    work_paid: Optional[bool] = Field(False, description="Работы оплачены")
    debt: Optional[int] = Field(None, description="Задолженность")
    debt_paid: Optional[bool] = Field(False, description="Задолженность оплачена")
    work_ids: Optional[List[int]] = Field(None, description="Список ID работ для привязки к заказу")

class OrderResponse(OrderRead):
    """Схема для ответа при создании заказа"""
    class Config:
        from_attributes = True


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
