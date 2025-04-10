# routers/order_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Integer
from sqlalchemy.orm import selectinload
from typing import List, Optional

from database import get_async_db
from models import Order, Counterparty
from schemas.order_schem import OrderSerial, OrderRead, PaginatedOrderResponse
from schemas.order_schem import OrderDetailResponse  # Импортируем новую схему

router = APIRouter(
    prefix="/order",
    tags=["order"],
)

@router.get("/read-serial", response_model=List[OrderSerial])
async def get_order_serials(
        status_id: Optional[int] = Query(None, description="Filter by status ID"),
        session: AsyncSession = Depends(get_async_db)
):
    """
    Получить список серийных номеров заказов с возможностью фильтрации по статусу.

    Параметры:
    - status_id: опциональный фильтр по ID статуса заказа

    Возвращает: список объектов OrderSerial, содержащих только серийный номер
    """
    query = select(Order.serial)

    # Применяем фильтр по статусу, если он указан
    if status_id is not None:
        query = query.where(Order.status_id == status_id)

    # Выполняем запрос
    result = await session.execute(query)
    serials = result.all()

    # Преобразуем результаты в нужный формат
    return [OrderSerial(serial=serial[0]) for serial in serials]

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
        selectinload(Order.customer).selectinload(Counterparty.form), # Загрузка контрагента и его формы
        selectinload(Order.works)  # Загрузка списка связанных работ
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
            # Передаем список ORM-объектов Work. Pydantic с `from_attributes=True`
            # и схемой WorkSchema преобразует их в список WorkSchema.
            "works": order.works,
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



@router.get("/detail/{serial}", response_model=OrderDetailResponse)
async def get_order_detail(
        serial: str,
        session: AsyncSession = Depends(get_async_db)
):
    """
    Получить подробную информацию о заказе, включая связанные комментарии, задачи и тайминги.

    Параметры:
    - serial: серийный номер заказа

    Возвращает: детальную информацию о заказе со всеми связями
    """
    # Запрос с жадной загрузкой всех необходимых связей
    query = select(Order).where(Order.serial == serial).options(
        selectinload(Order.customer).selectinload(Counterparty.form),
        selectinload(Order.works),
        selectinload(Order.comments),
        selectinload(Order.tasks),
        selectinload(Order.timings)
    )

    # Выполняем запрос
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Заказ с номером {serial} не найден")

    # Формируем customer_display_name
    customer_display_name = "Контрагент не указан"
    if order.customer:
        if order.customer.form:
            customer_display_name = f"{order.customer.form.name} {order.customer.name}"
        else:
            customer_display_name = order.customer.name

    # Создаем данные для ответа
    order_data = {
        "serial": order.serial,
        "name": order.name,
        "customer": customer_display_name,
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
        "works": order.works,
        "comments": order.comments,
        "tasks": order.tasks,
        "timings": order.timings
    }

    # Создаем и возвращаем объект Pydantic
    return OrderDetailResponse.model_validate(order_data)