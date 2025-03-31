# routers/person_router.py
"""
Тут функции - роутеры для работы с людьми (сотрудниками, представителями заказчиков и т.д.)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from uuid import UUID

from database import get_async_db
from models import Person
from schemas.person_schem import PersonCanBe, PersonResponse

router = APIRouter(
    prefix="/person",
    tags=["person"],
)


@router.get("/read", response_model=List[PersonCanBe])
async def get_people(
        can_be_any: Optional[bool] = Query(None, description="Filter by any can_be_* capability"),
        can_be_scheme_developer: Optional[bool] = Query(None, description="Filter by scheme development capability"),
        can_be_assembler: Optional[bool] = Query(None, description="Filter by assembly capability"),
        can_be_programmer: Optional[bool] = Query(None, description="Filter by programming capability"),
        can_be_tester: Optional[bool] = Query(None, description="Filter by testing capability"),
        active: Optional[bool] = Query(None, description="Filter by active status"),
        counterparty_id: Optional[int] = Query(None, description="Filter by counterparty ID"),
        session: AsyncSession = Depends(get_async_db)
):
    """
    Получить список людей с возможностью фильтрации по их свойствам.

    Параметры:
    - can_be_any: если True, выбирает людей у которых хотя бы одно свойство can_be_* равно True
    - can_be_scheme_developer: фильтр по возможности разрабатывать схемы
    - can_be_assembler: фильтр по возможности собирать
    - can_be_programmer: фильтр по возможности программировать
    - can_be_tester: фильтр по возможности тестировать
    - active: фильтр по активности
    - counterparty_id: фильтр по ID контрагента

    Возвращает: список объектов Person
    """
    query = select(Person)

    # Применяем фильтр "можно использовать хотя бы в одной роли"
    if can_be_any is True:
        query = query.where(
            or_(
                Person.can_be_scheme_developer == True,
                Person.can_be_assembler == True,
                Person.can_be_programmer == True,
                Person.can_be_tester == True
            )
        )

    # Применяем остальные фильтры по отдельным возможностям
    if can_be_scheme_developer is not None:
        query = query.where(Person.can_be_scheme_developer == can_be_scheme_developer)

    if can_be_assembler is not None:
        query = query.where(Person.can_be_assembler == can_be_assembler)

    if can_be_programmer is not None:
        query = query.where(Person.can_be_programmer == can_be_programmer)

    if can_be_tester is not None:
        query = query.where(Person.can_be_tester == can_be_tester)

    # Другие фильтры
    if active is not None:
        query = query.where(Person.active == active)

    if counterparty_id is not None:
        query = query.where(Person.counterparty_id == counterparty_id)

    # Выполняем запрос
    result = await session.execute(query)
    people = result.scalars().all()

    return people


@router.get("/{uuid}", response_model=PersonResponse)
async def get_person(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_db)
):
    """
    Получить информацию о конкретном человеке по его UUID.

    Параметры:
    - uuid: UUID человека

    Возвращает: объект Person
    """
    query = select(Person).where(Person.uuid == uuid)
    result = await session.execute(query)
    person = result.scalar_one_or_none()

    if person is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Person not found")

    return person