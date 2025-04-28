# counterparty_router.py
"""
все функции роутеры связанные с контрагентами
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from sqlalchemy.orm import joinedload

from models import Counterparty, CounterpartyForm
from database import get_async_db
from schemas.counterparty_schem import CounterpartyFormSchema, CounterpartySchema

router = APIRouter(
    prefix="/counterparty",
    tags=["counterparty"]
)


@router.get("/read", response_model=List[CounterpartySchema])
async def get_counterparties(session: AsyncSession = Depends(get_async_db)):
    """
    Получить всех контрагентов с формой (id и name)
    """
    # Выполняем запрос на получение контрагентов вместе с их формой
    result = await session.execute(
        select(Counterparty)
        .join(CounterpartyForm, Counterparty.form_id == CounterpartyForm.id)
        .options(
            # Используем sqlalchemy.orm.joinedload для eager loading
            # Это предотвратит N+1 проблему
            joinedload(Counterparty.form)
        )
    )

    # Получаем все результаты
    counterparties = result.scalars().all()

    # Возвращаем результаты, которые будут автоматически преобразованы
    # в список объектов CounterpartySchema
    return counterparties