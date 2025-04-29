# work_router.py
"""
Все функции роутеры связанные с работами по заказам
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from models import Work
from database import get_async_db
from schemas.work_schem import WorkSchema

router = APIRouter(
    prefix="/works",
    tags=["works"]
)


@router.get("/read-active", response_model=List[WorkSchema])
async def get_active_works(session: AsyncSession = Depends(get_async_db)):
    """
    Получить список всех активных работ по заказам (active=True)

    Returns:
        List[WorkSchema]: Список активных работ
    """
    try:
        # Выполняем запрос на получение активных работ
        result = await session.execute(
            select(Work)
            .where(Work.active == True)  # noqa: E712
            .order_by(Work.name)  # Опционально: сортировка по названию
        )

        # Получаем все результаты
        active_works = result.scalars().all()

        # Возвращаем результаты, которые будут автоматически преобразованы
        # в список объектов WorkSchema
        return active_works
    except Exception as e:
        # Логирование ошибки (можно добавить более подробное логирование)
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка работ: {str(e)}")