import asyncio

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Depends
from starlette.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

import uvicorn

#
# from database import async_session_maker, test_connection
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

from test_views import router as test_router
# from models.models import Country, Manufacturer


app = FastAPI(root_path="/api")
app.include_router(test_router)  # Добавляем роутер для тестовых запросов

# Настройка CORS
app.add_middleware(
    CORSMiddleware,  # type: ignore
    # allow_origins=["*"],  # Разрешить все источники (но это работает только для HTTP запросов)
    allow_origins=["https://voronovmaksim88-kis3-frontend-vue-v2-a3b1.twc1.net", "https://sibplc-kis3.ru"],
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
