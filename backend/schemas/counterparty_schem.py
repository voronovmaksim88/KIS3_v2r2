# counterparty_schem
"""
все функции роутеры связанные с контрагентами
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/counterparty",
    tags=["counterparty"]
)


# Схемы для сериализации данных контрагентов с формой
class CounterpartyFormSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # вместо orm_mode = True

class CounterpartySchema(BaseModel):
    id: int
    name: str
    form: CounterpartyFormSchema

    class Config:
        from_attributes = True  # вместо orm_mode = True