# main.py
"""
главный файл
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

import uvicorn
from models import *
from auth import jwt_auth

from routers.test_views import router as test_router
from routers import import_router
from routers.box_accountig_router import router as box_accountig_router

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from database import get_async_db
from models import User as UserModel
from auth.jwt_auth import get_current_auth_user

app = FastAPI(root_path="/api")

# Подключаем роутеры
app.include_router(import_router.router)  # роутер для импорта данных
app.include_router(test_router)  # роутер для тестовых запросов
app.include_router(jwt_auth.router)
app.include_router(box_accountig_router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["https://sibplc-kis3.ru", "http://localhost:3000", "http://localhost:80", "http://localhost",
                   'http://localhost:8000', 'http://localhost:5173', 'http://localhost:5174'],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# для автоматического перезапуска приложения при изменении кода
if __name__ == "__main__":
    # uvicorn.run("main:app", reload=True)
    # asyncio.run(test_connection())

    # прямой доступ всем желающим минуя NGINX прям по HTTP
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

    # Доступ только из localhost. NGINX будет передавать запросы на 127.0.0.1:8000
    # более безопасный подход для production
    uvicorn.run("main:app", reload=True)


async def _fetch_list(
        db: AsyncSession,
        current_user: UserModel,
        model: type,
        list_name: str,
        fields: list[str]
):
    """Общая функция для получения списков сущностей"""
    if not current_user:
        logger.warning(f"Unauthorized access attempt to {list_name} list")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    logger.debug(f"User {current_user.username} requesting all {list_name}")

    try:
        # Выполняем запрос для получения всех записей
        query = select(model)
        result = await db.execute(query)
        items = result.scalars().all()

        # Преобразуем результат в список словарей
        items_list = [
            {field: getattr(item, field) for field in fields}
            for item in items
        ]

        logger.info(f"Successfully retrieved {len(items_list)} {list_name} for user {current_user.username}")
        return {list_name: items_list}

    except Exception as e:
        logger.error(f"Error fetching {list_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch {list_name}: {str(e)}"
        )


@app.get("/")
def home():
    """Домашняя страница"""
    html_content = "<h2>FastAPI is the best backend framework</h2>"
    html_content += '<p>Интерактивная документация на <a href="/api/docs">  /api/docs  </a></p>'
    return HTMLResponse(content=html_content)


# Пояснения:
# 1. Это асинхронная функция-генератор, которая используется как зависимость в FastAPI
# 2. async_session_maker - это, фабрика для создания асинхронных сессий SQLAlchemy
# 3. Менеджер контекста (with) обеспечивает правильное открытие и закрытие сессии
# 4. yield используется вместо return, чтобы сделать эту функцию генератором.
# Такой подход обеспечивает эффективное управление соединениями с базой данных в асинхронном контексте,
# гарантируя, что каждый запрос получает свежую сессию, которая правильно закрывается после использования.


# далее будут функции которые будут доставать данные из базы данных, их надо потом будет вынести в отдельный файл,
# и создать отдельный роутер


@app.get("/all_countries")
async def get_all_countries(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех стран.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=Country,
        list_name="countries",
        fields=["id", "name"]
    )


@app.get("/all_manufacturers")
async def get_all_manufacturers(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех производителей.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=Manufacturer,
        list_name="manufacturers",
        fields=["id", "name", "country_id"]
    )


@app.get("/all_equipment_types")
async def get_all_equipment_types(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех типов оборудования.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=EquipmentType,
        list_name="equipment_types",
        fields=["id", "name"]
    )


@app.get("/all_currencies")
async def get_all_currencies(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех валют.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=Currency,
        list_name="currencies",
        fields=["id", "name"]
    )


@app.get("/all_cities")
async def get_all_cities(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех городов.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=City,
        list_name="cities",
        fields=["id", "name", "country_id"]
    )


@app.get("/all_counterparty_forms")
async def get_all_counterparty_forms(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех форм контрагентов.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=CounterpartyForm,
        list_name="counterparty_forms",
        fields=["id", "name"]
    )


@app.get("/all_counterparties")
async def get_all_counterparties(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех контрагентов.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to counterparties list")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} requesting all counterparties")

        # Выполняем запрос для получения всех контрагентов
        query = select(Counterparty)
        result = await db.execute(query)

        # Получаем все записи
        counterparties = result.scalars().all()

        # Преобразуем результат в список словарей
        counterparties_list = [
            {
                "id": counterparty.id,
                "name": counterparty.name,
                "note": counterparty.note,
                "city_id": counterparty.city_id,
                "form_id": counterparty.form_id
            }
            for counterparty in counterparties
        ]

        logger.info(
            f"Successfully retrieved {len(counterparties_list)} counterparties for user {current_user.username}")
        return {"counterparties_list": counterparties_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching counterparties: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch counterparties: {str(e)}"
        )


@app.get("/all_people")
async def get_all_people(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех людей.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to people list")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} requesting all people")

        # Выполняем запрос для получения всех людей
        query = select(Person)
        result = await db.execute(query)

        # Получаем все записи
        people = result.scalars().all()

        # Преобразуем результат в список словарей
        people_list = [
            {
                "uuid": person.uuid,
                "name": person.name,
                "patronymic": person.patronymic,
                "surname": person.surname,
                "phone": person.phone,
                "email": person.email,
                "counterparty_id": person.counterparty_id,
                "birth_date": person.birth_date,
                "active": person.active,
                "note": person.note,
            }
            for person in people
        ]

        logger.info(f"Successfully retrieved {len(people_list)} people for user {current_user.username}")
        return {"people_list": people_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching people: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch people: {str(e)}"
        )


@app.get("/all_works")
async def get_all_works(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех видов работ.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=Work,
        list_name="works",
        fields=["id", "name", "description", "active"]
    )


@app.get("/all_order_statuses")
async def get_all_order_statuses(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех статусов заказов.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=OrderStatus,
        list_name="order_statuses",
        fields=["id", "name", "description"]
    )


@app.get("/all_orders")
async def get_all_orders(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех заказов.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to orders list")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} requesting all orders")

        query = select(Order)
        result = await db.execute(query)
        orders = result.scalars().all()

        orders_list = [
            {
                "serial": order.serial,
                "name": order.name,
                "customer_id": order.customer_id,
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
                "debt_paid": order.debt_paid
            }
            for order in orders
        ]

        logger.info(f"Successfully retrieved {len(orders_list)} orders for user {current_user.username}")
        return {"orders": orders_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )


@app.get("/all_box_accounting")
async def get_all_box_accounting(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех записей учета шкафов.
    Требует аутентификации пользователя.
    """
    return await _fetch_list(
        db=db,
        current_user=current_user,
        model=BoxAccounting,
        list_name="boxes",
        fields=["serial_num",
                "name",
                "order_id",
                "scheme_developer_id",
                "assembler_id",
                "programmer_id",
                "tester_id"
                ]
    )


@app.get("/all_order_comments")
async def get_all_order_comments(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех комментариев к заказам.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to order comments list")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} requesting all order comments")

        query = select(OrderComment)
        result = await db.execute(query)
        comments = result.scalars().all()

        comments_list = [
            {
                "id": comment.id,
                "order_id": comment.order_id,
                "moment_of_creation": comment.moment_of_creation.isoformat() if comment.moment_of_creation else None,
                "text": comment.text,
                "person_uuid": comment.person_uuid
            }
            for comment in comments
        ]

        logger.info(f"Successfully retrieved {len(comments_list)} order comments for user {current_user.username}")
        return {"order_comments": comments_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order comments: {str(e)}"
        )


@app.get("/all_control_cabinets")
async def get_all_control_cabinets(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех шкафов управления.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to control cabinets list")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} requesting all control cabinets")

        # Выполняем запрос для получения всех шкафов управления
        query = select(ControlCabinet)
        result = await db.execute(query)

        # Получаем все записи
        cabinets = result.scalars().all()

        # Преобразуем результат в список словарей
        cabinets_list = [
            {
                "id": cabinet.id,
                "name": cabinet.name,
                "model": cabinet.model,
                "vendor_code": cabinet.vendor_code,
                "description": cabinet.description,
                "type_id": cabinet.type_id,
                "manufacturer_id": cabinet.manufacturer_id,
                "equipment_type_id": cabinet.type_id,
                "price": cabinet.price,
                "currency_id": cabinet.currency_id,
                "relevance": cabinet.relevance,
                "price_date": cabinet.price_date,
                "material_id": cabinet.material_id,
                "ip_id": cabinet.ip_id,
                "height": cabinet.height,
                "width": cabinet.width,
                "depth": cabinet.depth
            }
            for cabinet in cabinets
        ]

        logger.info(f"Successfully retrieved {len(cabinets_list)} control cabinets for user {current_user.username}")
        return {"control_cabinets": cabinets_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching control cabinets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch control cabinets: {str(e)}"
        )


@app.get("/all_tasks")
async def get_all_tasks(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех задач.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to tasks list")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} requesting all tasks")

        # Выполняем запрос для получения всех задач
        query = select(Task)
        result = await db.execute(query)

        # Получаем все записи
        tasks = result.scalars().all()

        # Преобразуем результат в список словарей
        tasks_list = [
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "status_id": task.status_id,
                "payment_status_id": task.payment_status_id,
                "executor_id": task.executor_id,
                "planned_duration": str(task.planned_duration) if task.planned_duration else None,
                "actual_duration": str(task.actual_duration) if task.actual_duration else None,
                "creation_moment": task.creation_moment.isoformat() if task.creation_moment else None,
                "start_moment": task.start_moment.isoformat() if task.start_moment else None,
                "deadline_moment": task.deadline_moment.isoformat() if task.deadline_moment else None,
                "end_moment": task.end_moment.isoformat() if task.end_moment else None,
                "price": task.price,
                "order_serial": task.order_serial,
                "parent_task_id": task.parent_task_id,
                "root_task_id": task.root_task_id
            }
            for task in tasks
        ]

        logger.info(f"Successfully retrieved {len(tasks_list)} tasks for user {current_user.username}")
        return {"tasks": tasks_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@app.get("/all_timings")
async def get_all_timings(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user)
):
    """
    Функция для получения всех тайминговых записей.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to timings list")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} requesting all timings")

        # Выполняем запрос для получения всех тайминговых записей
        query = select(Timing)
        result = await db.execute(query)

        # Получаем все записи
        timings = result.scalars().all()

        # Преобразуем результат в список словарей
        timings_list = [
            {
                "id": timing.id,
                "order_serial": timing.order_serial,
                "task_id": timing.task_id,
                "executor_id": timing.executor_id,
                "time": str(timing.time) if timing.time else None,  # Преобразуем timedelta в строку
                "timing_date": timing.timing_date.isoformat() if timing.timing_date else None
            }
            for timing in timings
        ]

        logger.info(f"Successfully retrieved {len(timings_list)} timings for user {current_user.username}")
        return {"timings": timings_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching timings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch timings: {str(e)}"
        )
