# routers/order_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Integer
from sqlalchemy.orm import selectinload
from typing import List, Optional

from database import get_async_db
from models import Order, Counterparty
from schemas.order_schem import OrderSerial, OrderRead, PaginatedOrderResponse

router = APIRouter(
    prefix="/order",
    tags=["order"],
)

# --- Роутер /read-serial остается без изменений ---
@router.get("/read-serial", response_model=List[OrderSerial])
# ... (код без изменений) ...

@router.get("/read", response_model=PaginatedOrderResponse)
async def read_orders(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return per page"),
    status_id: Optional[int] = Query(None, description="Filter by status ID"),
    search_serial: Optional[str] = Query(None, description="Search by order serial (case-insensitive, partial match)"),
    search_customer: Optional[str] = Query(None, description="Search by customer name (case-insensitive, partial match)"),
    search_priority: Optional[int] = Query(None, description="Search by exact priority value"),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Получить список заказов с пагинацией, фильтрацией и поиском.
    Поле customer возвращает строку 'Форма Имя'.
    Заказы отсортированы по дате (из serial) - от старых к новым.
    """

    # Запрос с жадной загрузкой связей
    query = select(Order).options(
        selectinload(Order.customer).selectinload(Counterparty.form)
    )
    # Запрос для подсчета
    count_query = select(func.count(Order.serial))

    # --- Применение JOIN для ФИЛЬТРАЦИИ ---
    if search_customer:
        query = query.join(Order.customer)
        count_query = count_query.join(Order.customer)

    # --- Применение фильтров и поиска ---
    # ... (код фильтров status_id, search_serial, search_customer, search_priority) ...
    if status_id is not None:
        # ... validation and where clause ...
        query = query.where(Order.status_id == status_id)
        count_query = count_query.where(Order.status_id == status_id)
    if search_serial:
        # ... where clause ...
        query = query.where(Order.serial.ilike(f"%{search_serial}%"))
        count_query = count_query.where(Order.serial.ilike(f"%{search_serial}%"))
    if search_customer:
        # ... where clause on Counterparty.name ...
        query = query.where(Counterparty.name.ilike(f"%{search_customer}%"))
        count_query = count_query.where(Counterparty.name.ilike(f"%{search_customer}%"))
    if search_priority is not None:
        # ... validation and where clause ...
        query = query.where(Order.priority == search_priority)
        count_query = count_query.where(Order.priority == search_priority)


    # --- Выполнение запроса на подсчет общего количества ---
    total_result = await session.execute(count_query)
    total = total_result.scalar_one_or_none() or 0

    # --- Применение НОВОЙ сортировки и пагинации. ---
    # Заменяем старую сортировку query = query.order_by(Order.serial)
    # на сортировку по частям serial: Год (9-12), Месяц (5-6), Номер (1-3)
    query = query.order_by(
        cast(func.substring(Order.serial, 9, 4), Integer).asc(), # Сортировка по году (возрастание)
        cast(func.substring(Order.serial, 5, 2), Integer).asc(), # Сортировка по месяцу (возрастание)
        cast(func.substring(Order.serial, 1, 3), Integer).asc()  # Сортировка по номеру (возрастание)
    )
    # Применяем пагинацию
    query = query.offset(skip).limit(limit)

    # --- Выполнение основного запроса ---
    result = await session.execute(query)
    orders_orm = result.scalars().unique().all() # Получаем ORM объекты Order

    # --- Ручное формирование списка данных для ответа ---
    orders_data_list = []
    for order in orders_orm:
        # Формируем строку customer с проверками
        customer_display_name = "Контрагент не указан" # Значение по умолчанию
        if order.customer: # Проверяем, что связь customer загружена и не None
            if order.customer.form: # Проверяем, что связь form у customer загружена и не None
                customer_display_name = f"{order.customer.form.name} {order.customer.name}"
            else:
                # Если формы нет, используем только имя контрагента
                customer_display_name = order.customer.name

        # Создаем словарь для Pydantic модели OrderRead
        order_data = {
            "serial": order.serial,
            "name": order.name,
            "customer": customer_display_name, # Подставляем сформированную строку
            "priority": order.priority,
            "status_id": order.status_id,
            "start_moment": order.start_moment,
            "deadline_moment": order.deadline_moment,
            "end_moment": order.end_moment,
            "materials_cost": order.materials_cost,
            "materials_paid": order.materials_paid,
            "products_cost": order.products_cost,
            "products_paid": order.products_paid,
            "work_cost": order.work_cost,
            "work_paid": order.work_paid,
            "debt": order.debt,
            "debt_paid": order.debt_paid,
        }
        # Добавляем валидированный Pydantic объект в список
        # Pydantic сам проверит типы остальных полей из словаря
        orders_data_list.append(OrderRead.model_validate(order_data))

    # --- Возврат результата ---
    return PaginatedOrderResponse(
        total=total,
        limit=limit,
        skip=skip,
        data=orders_data_list # Передаем сформированный список Pydantic объектов
    )