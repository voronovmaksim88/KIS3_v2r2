from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from starlette.responses import HTMLResponse

import uvicorn

from database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from test_views import router as test_router
from models.models import Country, Manufacturer, EquipmentType, Currency, City

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
        # Выполняем запрос для получения всех производителей
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
