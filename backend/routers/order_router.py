# routers/order_router.py
from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Integer
from sqlalchemy.orm import selectinload
from typing import List, Optional

from database import get_async_db

# Импортируем модели SQLAlchemy
from models import Order, Counterparty, Person, OrderStatus, Work

from schemas.order_schem import OrderSerial, OrderRead, PaginatedOrderResponse, OrderCommentSchema, OrderResponse, \
    OrderCreate
from schemas.order_schem import OrderDetailResponse  # Импортируем новую схему

# Импортируем другие необходимые схемы, если они используются в OrderDetailResponse
from schemas.work_schem import WorkSchema
from schemas.task_schem import TaskSchema
from schemas.timing_schem import TimingSchema
from datetime import datetime

from fastapi import status

router = APIRouter(
    prefix="/order",
    tags=["order"],
)


async def generate_order_serial(
        session: AsyncSession,
        current_date: Optional[datetime] = None
) -> str:
    """
    Генерирует уникальный серийный номер заказа в формате NNN-MM-YYYY

    Параметры:
    - session: AsyncSession для работы с БД
    - current_date: опциональная дата для генерации (по умолчанию текущая дата)

    Возвращает:
    - строку с серийным номером в формате "NNN-MM-YYYY"
    """
    if current_date is None:
        current_date = datetime.now()

    current_month = current_date.month
    current_year = current_date.year

    # Находим максимальный порядковый номер для текущего года
    max_serial_query = select(
        func.max(func.substring(Order.serial, 1, 3).cast(Integer))
    ).where(
        func.substring(Order.serial, 8, 4) == str(current_year)
    )

    result = await session.execute(max_serial_query)
    max_serial = result.scalar_one_or_none()

    # Если заказов в этом году еще не было, начинаем с 1
    order_number = (max_serial or 0) + 1

    # Форматируем номер заказа
    return f"{order_number:03d}-{current_month:02d}-{current_year}"


@router.get("/new-serial", response_model=OrderSerial)
async def generate_new_order_serial(
        session: AsyncSession = Depends(get_async_db)
):
    """
    Генерирует и возвращает новый серийный номер заказа в формате NNN-MM-YYYY

    Возвращает:
    - объект OrderSerial с полем serial (строка в формате "NNN-MM-YYYY")
    """
    try:
        serial = await generate_order_serial(session)
        return OrderSerial(serial=serial)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации номера заказа: {str(e)}"
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
        show_ended: bool = Query(True, description="Show completed orders (status 5, 6, 7)"),
        # По умолчанию True, чтобы показывать все заказы
        status_id: Optional[int] = Query(None, description="Filter by status ID"),
        search_serial: Optional[str] = Query(None,
                                             description="Search by order serial (case-insensitive, partial match)"),
        search_customer: Optional[str] = Query(None,
                                               description="Search by customer name (case-insensitive, partial match)"),
        search_priority: Optional[int] = Query(None, description="Search by exact priority value"),
        session: AsyncSession = Depends(get_async_db)
):
    """
    Получить список заказов с пагинацией, фильтрацией и поиском.
    Поле customer возвращает строку 'Форма Название'.
    Заказы отсортированы по дате (из serial) - от старых к новым.

    Параметр show_ended:
    - Если True (по умолчанию), показывает все заказы
    - Если False, исключает заказы со статусами 5, 6, 7 (завершенные)
    """

    # Запрос с жадной загрузкой связей
    query = select(Order).options(
        selectinload(Order.customer).selectinload(Counterparty.form),  # Загрузка контрагента и его формы
        selectinload(Order.works)  # Загрузка списка связанных работ
    )

    # Запрос для подсчета
    count_query = select(func.count(Order.serial))

    # --- Применение JOIN для ФИЛЬТРАЦИИ ---
    if search_customer:
        query = query.join(Order.customer)
        count_query = count_query.join(Order.customer)

    # --- Применение фильтров и поиска ---

    # Фильтрация завершенных заказов (новый функционал)
    if show_ended is False:  # Проверяем именно на False, чтобы None не вызывал фильтрацию
        # Исключаем заказы со статусами 5, 6, 7 (завершенные)
        completed_statuses = [5, 6, 7]  # "Выполнено в срок", "Выполнено НЕ в срок", "Не согласовано"
        query = query.where(~Order.status_id.in_(completed_statuses))
        count_query = count_query.where(~Order.status_id.in_(completed_statuses))

    # Применение остальных фильтров
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
        cast(func.substring(Order.serial, 9, 4), Integer).asc(),  # Сортировка по году (возрастание)
        cast(func.substring(Order.serial, 5, 2), Integer).asc(),  # Сортировка по месяцу (возрастание)
        cast(func.substring(Order.serial, 1, 3), Integer).asc()  # Сортировка по номеру (возрастание)
    )
    # Применяем пагинацию
    query = query.offset(skip).limit(limit)

    # --- Выполнение основного запроса ---
    result = await session.execute(query)
    orders_orm = result.scalars().unique().all()  # Получаем ORM объекты Order

    # --- Ручное формирование списка данных для ответа ---
    orders_data_list = []
    for order in orders_orm:
        # Формируем строку customer с проверками
        customer_display_name = "Контрагент не указан"  # Значение по умолчанию
        if order.customer:  # Проверяем, что связь customer загружена и не None
            if order.customer.form:  # Проверяем, что связь form у customer загружена и не None
                customer_display_name = f"{order.customer.form.name} {order.customer.name}"
            else:
                # Если формы нет, используем только имя контрагента
                customer_display_name = order.customer.name

        # Создаем словарь для Pydantic модели OrderRead
        order_data = {
            "serial": order.serial,
            "name": order.name,
            "customer": customer_display_name,  # Подставляем сформированную строку
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
        data=orders_data_list  # Передаем сформированный список Pydantic объектов
    )


@router.get("/detail/{serial}", response_model=OrderDetailResponse)
async def get_order_detail(
        serial: str,
        session: AsyncSession = Depends(get_async_db)
):
    """
    Получить подробную информацию о заказе, включая связанные комментарии, задачи и тайминги.
    Для комментариев возвращает ФИО автора.
    Для задач возвращает ФИО исполнителя.

    Параметры:
    - serial: серийный номер заказа

    Возвращает: детальную информацию о заказе со всеми связями
    """
    # Запрос с жадной загрузкой всех необходимых связей, КРОМЕ Person для комментариев и исполнителей задач
    # Мы загрузим Person для комментариев и исполнителей задач отдельными запросами после получения заказа
    query = select(Order).where(Order.serial == serial).options(
        selectinload(Order.customer).selectinload(Counterparty.form),
        selectinload(Order.works),
        selectinload(Order.comments),  # Загружаем комментарии как есть
        selectinload(Order.tasks),
        selectinload(Order.timings)
    )

    # Выполняем запрос
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с номером {serial} не найден")

    # --- Формирование данных для ответа ---

    # 1. Формируем customer_display_name
    customer_display_name = "Контрагент не указан"
    if order.customer:
        if order.customer.form:
            customer_display_name = f"{order.customer.form.name} {order.customer.name}"
        else:
            customer_display_name = order.customer.name

    # 2. Обработка комментариев для получения ФИО автора
    formatted_comments = []
    if order.comments:
        # Собираем уникальные UUID авторов комментариев
        author_uuids = {comment.person_uuid for comment in order.comments if comment.person_uuid}

        authors_map = {}
        if author_uuids:
            # Загружаем данные авторов одним запросом
            person_query = select(Person).where(Person.uuid.in_(author_uuids))
            person_results = await session.execute(person_query)
            # Создаем словарь {uuid: "Фамилия Имя Отчество"}
            for person in person_results.scalars():
                fio = f"{person.surname} {person.name}"
                if person.patronymic:
                    fio += f" {person.patronymic}"
                authors_map[person.uuid] = fio

        # Формируем список комментариев с ФИО автора
        for comment in order.comments:
            author_name = authors_map.get(comment.person_uuid, "Автор не найден")  # Имя по умолчанию
            formatted_comments.append(
                OrderCommentSchema(
                    id=comment.id,
                    moment_of_creation=comment.moment_of_creation,
                    text=comment.text,
                    person=author_name  # Подставляем ФИО
                )
            )

    # 3. Обработка задач для получения ФИО исполнителя
    formatted_tasks = []
    if order.tasks:
        # Собираем уникальные UUID исполнителей задач
        executor_uuids = {task.executor_uuid for task in order.tasks if task.executor_uuid}

        executors_map = {}
        if executor_uuids:
            # Загружаем данные исполнителей одним запросом
            person_query = select(Person).where(Person.uuid.in_(executor_uuids))
            person_results = await session.execute(person_query)
            # Создаем словарь {uuid: "Фамилия Имя Отчество"}
            for person in person_results.scalars():
                fio = f"{person.surname} {person.name}"
                if person.patronymic:
                    fio += f" {person.patronymic}"
                executors_map[person.uuid] = fio

        # Формируем список задач с ФИО исполнителя
        for task in order.tasks:
            executor_name = executors_map.get(task.executor_uuid,
                                              "Исполнитель не назначен") if task.executor_uuid else "Исполнитель не назначен"

            # Создаем словарь с данными задачи, включая ФИО исполнителя
            task_dict = {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "status_id": task.status_id,
                "payment_status_id": task.payment_status_id,
                "executor": executor_name,  # Подставляем ФИО исполнителя
                "planned_duration": task.planned_duration,
                "actual_duration": task.actual_duration,
                "creation_moment": task.creation_moment,
                "start_moment": task.start_moment,
                "deadline_moment": task.deadline_moment,
                "end_moment": task.end_moment,
                "price": task.price,
                "parent_task_id": task.parent_task_id,
                "root_task_id": task.root_task_id
            }

            # Добавляем задачу в список
            formatted_tasks.append(TaskSchema.model_validate(task_dict))

    # 4. Подготовка остальных данных
    works_data = [WorkSchema.model_validate(w) for w in order.works]
    timings_data = [TimingSchema.model_validate(ti) for ti in order.timings]

    # 5. Создаем словарь данных для основного ответа
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
        "works": works_data,
        "comments": formatted_comments,  # Используем отформатированные комментарии
        "tasks": formatted_tasks,  # Используем отформатированные задачи
        "timings": timings_data
    }

    # 6. Создаем и возвращаем объект Pydantic response_model
    # Pydantic сам проверит соответствие словаря order_data схеме OrderDetailResponse
    return OrderDetailResponse.model_validate(order_data)


@router.post("/create", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
        order_data: OrderCreate,
        session: AsyncSession = Depends(get_async_db)
):
    """
    Создает новый заказ (Order).

    Параметры:
    - order_data: данные для создания заказа

    Возвращает: созданный заказ с полной информацией
    """
    # Проверяем существование контрагента
    counterparty_query = select(Counterparty).where(Counterparty.id == order_data.customer_id)
    result = await session.execute(counterparty_query)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контрагент с ID {order_data.customer_id} не найден"
        )

    # Проверяем существование статуса заказа
    status_query = select(OrderStatus).where(OrderStatus.id == order_data.status_id)
    result = await session.execute(status_query)
    order_status = result.scalar_one_or_none()
    if not order_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Статус заказа с ID {order_data.status_id} не найден"
        )

    # Генерируем серийный номер заказа в формате NNN-MM-YYYY
    serial = await generate_order_serial(session)

    # Создаем новый объект Order
    new_order = Order(
        serial=serial,
        name=order_data.name,
        customer_id=order_data.customer_id,
        priority=order_data.priority,
        status_id=order_data.status_id,
        start_moment=order_data.start_moment or datetime.now(),
        deadline_moment=order_data.deadline_moment,
        end_moment=order_data.end_moment,
        materials_cost=order_data.materials_cost,
        materials_paid=order_data.materials_paid or False,
        products_cost=order_data.products_cost,
        products_paid=order_data.products_paid or False,
        work_cost=order_data.work_cost,
        work_paid=order_data.work_paid or False,
        debt=order_data.debt,
        debt_paid=order_data.debt_paid or False
    )

    # Добавляем связанные работы, если они указаны
    if order_data.work_ids:
        # Проверяем существование всех работ
        works_query = select(Work).where(Work.id.in_(order_data.work_ids))
        result = await session.execute(works_query)
        works = result.scalars().all()

        # Проверяем, что все запрошенные работы существуют
        found_work_ids = {work.id for work in works}
        missing_work_ids = set(order_data.work_ids) - found_work_ids
        if missing_work_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Работы с ID {missing_work_ids} не найдены"
            )

        # Связываем работы с заказом
        new_order.works = works

    # Сохраняем новый заказ
    session.add(new_order)
    await session.flush()  # Сохраняем заказ, но не коммитим транзакцию

    await session.commit()

    # Явно обновляем объект заказа и загружаем необходимые для ответа связи
    # attribute_names гарантирует, что эти связи будут загружены одним запросом (или несколькими эффективными)
    await session.refresh(new_order, attribute_names=["customer", "works"])

    # Если customer был загружен, то явно загружаем его связь 'form'
    if new_order.customer:
        await session.refresh(new_order.customer, attribute_names=["form"])

    # Теперь формирование имени безопасно, так как данные уже загружены
    customer_display_name = "Контрагент не указан"
    if new_order.customer:
        if new_order.customer.form:  # Доступ к .form теперь безопасен
            customer_display_name = f"{new_order.customer.form.name} {new_order.customer.name}"
        else:
            customer_display_name = new_order.customer.name

    # Создаем ответ с полной информацией о созданном заказе
    # Доступ к new_order.works также безопасен
    return OrderResponse(
        serial=new_order.serial,
        name=new_order.name,
        customer=customer_display_name,  # Передаем строку, как ожидает OrderResponse -> OrderRead
        priority=new_order.priority,
        status_id=new_order.status_id,
        start_moment=new_order.start_moment,
        deadline_moment=new_order.deadline_moment,
        end_moment=new_order.end_moment,
        materials_cost=new_order.materials_cost,
        materials_paid=new_order.materials_paid,
        products_cost=new_order.products_cost,
        products_paid=new_order.products_paid,
        work_cost=new_order.work_cost,
        work_paid=new_order.work_paid,
        debt=new_order.debt,
        debt_paid=new_order.debt_paid,
        # Используем model_validate (Pydantic V2) / from_orm (Pydantic V1)
        works=[WorkSchema.model_validate(work) for work in new_order.works],
    )