from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from starlette.responses import HTMLResponse

import uvicorn

from database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from test_views import router as test_router
from models.models import (Country, Manufacturer, EquipmentType, Currency, City, CounterpartyForm, Counterparty, Person,
                           Work, OrderStatus, Order, BoxAccounting)

app = FastAPI(root_path="/api")
app.include_router(test_router)  # Добавляем роутер для тестовых запросов

# Настройка CORS
app.add_middleware(
    CORSMiddleware,  # type: ignore
    # allow_origins=["*"],  # Разрешить все источники (но это работает только для HTTP запросов)
    allow_origins=["https://sibplc-kis3.ru", "http://localhost:3000", "http://localhost:80", "http://localhost",
                   'http://localhost:8000', 'http://localhost:5173'],
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


@app.get("/")
def home():
    """Домашняя страница"""
    html_content = "<h2>FastAPI is the best backend framework</h2>"
    html_content += '<p>Интерактивная документация на <a href="/api/docs">  /api/docs  </a></p>'
    return HTMLResponse(content=html_content)


#  Зависимость для получения сессии базы данных
async def get_db():
    # Используем асинхронный менеджер контекста для создания сессии
    async with async_session_maker() as session:
        # Возвращаем сессию через yield
        yield session


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
async def get_all_countries(db: AsyncSession = Depends(get_db)):
    try:
        # Создаем запрос для выборки всех стран
        query = select(Country)

        # Выполняем запрос
        result = await db.execute(query)

        # Получаем все записи
        countries = result.scalars().all()

        # Преобразуем результат в список словарей
        countries_list = [
            {
                "id": country.id,
                "name": country.name
            }
            for country in countries
        ]

        return {"countries": countries_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_manufacturers")
async def get_all_manufacturers(db: AsyncSession = Depends(get_db)):
    try:
        # Выполняем запрос для получения всех производителей
        query = select(Manufacturer)
        result = await db.execute(query)

        # Получаем все записи
        manufacturers = result.scalars().all()

        # Преобразуем результат в список словарей
        manufacturers_list = [
            {
                "id": manufacturer.id,
                "name": manufacturer.name,
                "country_id": manufacturer.country_id
            }
            for manufacturer in manufacturers
        ]

        return {"manufacturers": manufacturers_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_equipment_types")
async def get_all_equipment_types(db: AsyncSession = Depends(get_db)):
    try:
        # Выполняем запрос для получения всех производителей
        query = select(EquipmentType)
        result = await db.execute(query)

        # Получаем все записи
        equipment_types = result.scalars().all()

        # Преобразуем результат в список словарей
        equipment_types_list = [
            {
                "id": equipment_type.id,
                "name": equipment_type.name,
            }
            for equipment_type in equipment_types
        ]

        return {"equipment_types": equipment_types_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_currencies")
async def get_all_currencies(db: AsyncSession = Depends(get_db)):
    try:
        # Выполняем запрос для получения всех валют
        query = select(Currency)
        result = await db.execute(query)

        # Получаем все записи
        currencies = result.scalars().all()

        # Преобразуем результат в список словарей
        currencies_list = [
            {
                "id": currency.id,
                "name": currency.name,
            }
            for currency in currencies
        ]

        return {"currencies_list": currencies_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_cities")
async def get_all_cities(db: AsyncSession = Depends(get_db)):
    try:
        # Выполняем запрос для получения всех городов
        query = select(City)
        result = await db.execute(query)

        # Получаем все записи
        cities = result.scalars().all()

        # Преобразуем результат в список словарей
        cities_list = [
            {
                "id": city.id,
                "name": city.name,
                "country_id": city.country_id  # Если нужно возвратить country_id
            }
            for city in cities
        ]

        return {"cities_list": cities_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_counterparty_forms")
async def get_all_counterparty_forms(db: AsyncSession = Depends(get_db)):
    try:
        # Выполняем запрос для получения всех форм контрагентов
        query = select(CounterpartyForm)
        result = await db.execute(query)

        # Получаем все записи
        counterparty_forms = result.scalars().all()

        # Преобразуем результат в список словарей
        counterparty_forms_list = [
            {
                "id": form.id,
                "name": form.name,
            }
            for form in counterparty_forms
        ]

        return {"counterparty_forms_list": counterparty_forms_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_counterparties")
async def get_all_counterparties(db: AsyncSession = Depends(get_db)):
    try:
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

        return {"counterparties_list": counterparties_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_people")
async def get_all_people(db: AsyncSession = Depends(get_db)):
    try:
        # Выполняем запрос для получения всех людей
        query = select(Person)
        result = await db.execute(query)

        # Получаем все записи
        people = result.scalars().all()

        # Преобразуем результат в список словарей
        people_list = [
            {
                "id": person.id,
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

        return {"people_list": people_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_works")
async def get_all_works(db: AsyncSession = Depends(get_db)):
    try:
        query = select(Work)
        result = await db.execute(query)
        works = result.scalars().all()

        works_list = [
            {
                "id": work.id,
                "name": work.name,
                "description": work.description,
                "active": work.active
            }
            for work in works
        ]

        return {"works": works_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_order_statuses")
async def get_all_order_statuses(db: AsyncSession = Depends(get_db)):
    try:
        query = select(OrderStatus)
        result = await db.execute(query)
        order_statuses = result.scalars().all()

        order_statuses_list = [
            {
                "id": status.id,
                "name": status.name,
                "description": status.description
            }
            for status in order_statuses
        ]

        return {"order_statuses": order_statuses_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_orders")
async def get_all_orders(db: AsyncSession = Depends(get_db)):
    try:
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

        return {"orders": orders_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/all_boxes")
async def get_all_boxes(db: AsyncSession = Depends(get_db)):
    try:
        query = select(BoxAccounting)
        result = await db.execute(query)
        boxes = result.scalars().all()

        boxes_list = [
            {
                "serial_num": box.serial_num,
                "name": box.name,
                "order_id": box.order_id,
                "scheme_developer_id": box.scheme_developer_id,
                "assembler_id": box.assembler_id,
                "programmer_id": box.programmer_id,
                "tester_id": box.tester_id
            }
            for box in boxes
        ]

        return {"boxes": boxes_list}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
