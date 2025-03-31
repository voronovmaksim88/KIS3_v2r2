# main.py
"""
главный файл
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

import uvicorn
from auth import jwt_auth

from routers.test_views import router as test_router
from routers.import_router import router as import_router
from routers.box_accountig_router import router as box_accountig_router
from routers.get_all_router import router as get_all_router
from routers.order_router import router as order_router
from routers.people_router import router as people_router

app = FastAPI(root_path="/api")

# Подключаем роутеры
app.include_router(import_router)  # роутер для импорта данных
app.include_router(test_router)  # роутер для тестовых запросов
app.include_router(jwt_auth.router)
app.include_router(box_accountig_router)
app.include_router(get_all_router)
app.include_router(order_router)
app.include_router(people_router)

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


@app.get("/")
def home():
    """Домашняя страница"""
    html_content = "<h2>FastAPI is the best backend framework</h2>"
    html_content += '<p>Интерактивная документация на <a href="/api/docs">  /api/docs  </a></p>'
    return HTMLResponse(content=html_content)
