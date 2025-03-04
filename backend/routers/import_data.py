from KIS2.DjangoRestAPI import get_countries_set as get_countries_set_from_kis2

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
                           Work, OrderStatus, Order, BoxAccounting, OrderComment)

kis2_countries_set = get_countries_set_from_kis2()


#  Зависимость для получения сессии базы данных
async def get_db():
    # Используем асинхронный менеджер контекста для создания сессии
    async with async_session_maker() as session:
        # Возвращаем сессию через yield
        yield session


async def import_countries(db: AsyncSession = Depends(get_db)):
    try:
        # Создаем запрос для выборки всех стран
        query = select(Country)

        # Выполняем запрос
        result = await db.execute(query)

        # Получаем все записи
        countries = result.scalars().all()

        # Преобразуем результат в множество имен стран
        kis3_countries_set = {country.name for country in countries}

        return {"countries": list(kis3_countries_set)}  # Преобразуем обратно в список для JSON-сериализации
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
