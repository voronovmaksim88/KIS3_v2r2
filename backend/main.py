# main.py
"""
главный файл
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from sqlalchemy import text  # Импортируем text для запроса

import uvicorn
from auth import jwt_auth

from routers.test_views import router as test_router
from routers.import_router import router as import_router
from routers.box_accountig_router import router as box_accountig_router
from routers.get_all_router import router as get_all_router
from routers.order_router import router as order_router
from routers.people_router import router as people_router
from routers.counterparty_router import router as counterparty_router
from routers.work_router import router as work_router
from routers.comments_router import router as comments_router

# Импортируем фабрику сессий из вашего модуля database
from database import async_session_maker

# --- Конфигурация логирования ---
# настроим базовый логгер для вывода информации о фоновой задаче
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# --- Конец Конфигурации логирования ---


# --- Фоновая задача для поддержания соединения с БД ---
async def keep_db_connection_alive(interval_seconds: int = 60):
    """
    Периодически выполняет простой запрос к БД для поддержания активности соединения.
    """
    logger.info(f"Starting database keep-alive task with {interval_seconds}s interval.")
    while True:
        try:
            async with async_session_maker() as session:
                # Выполняем очень легкий запрос
                await session.execute(text("SELECT 1"))
            # Логируем успешное выполнение только при необходимости (можно закомментировать)
            # logger.debug("Database keep-alive ping successful.")
        except asyncio.CancelledError:
            logger.info("Database keep-alive task received cancellation request.")
            # Позволяем циклу завершиться естественно при отмене
            break
        except Exception as e:
            # Логируем ошибку, но продолжаем работу задачи
            logger.error(f"Database keep-alive ping failed: {e}", exc_info=True)  # exc_info=True добавит traceback

        # Ждем перед следующим пингом.
        # Используем try/except для корректной обработки отмены во время сна
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Database keep-alive task cancelled during sleep.")
            break  # Выходим из цикла при отмене
    logger.info("Database keep-alive task finished.")


@asynccontextmanager
# async def lifespan(app: FastAPI): # <-- Можно и так, если не мешает предупреждение линтера
async def lifespan(_: FastAPI): # <-- Вот так, чтобы показать, что app не используется
    """
    Менеджер жизненного цикла FastAPI для запуска и остановки фоновых задач.
    """
    logger.info("Application startup: Initializing keep-alive task...")
    # Запускаем задачу поддержания соединения с БД в фоне.
    # Устанавливаем интервал, например, 55 секунд (чуть меньше стандартных таймаутов)
    keep_alive_task = asyncio.create_task(keep_db_connection_alive(interval_seconds=55))

    yield  # Приложение работает здесь

    # Код после yield выполняется при остановке приложения
    logger.info("Application shutdown: Stopping keep-alive task...")
    # Отправляем сигнал отмены задаче
    keep_alive_task.cancel()
    try:
        # Ждем завершения задачи (она должна обработать CancelledError)
        await keep_alive_task
    except asyncio.CancelledError:
        # Это ожидаемое исключение при отмене
        logger.info("Keep-alive task successfully cancelled and stopped.")
    except Exception as e:
        # Логируем непредвиденные ошибки при остановке задачи
        logger.error(f"Error stopping keep-alive task: {e}", exc_info=True)
    logger.info("Application shutdown complete.")


# --- Конец фоновой задачи ---


# Создаем приложение FastAPI с lifespan менеджером
app = FastAPI(root_path="/api", lifespan=lifespan)


app.include_router(comments_router)
app.include_router(import_router)
app.include_router(test_router)
app.include_router(jwt_auth.router)
app.include_router(box_accountig_router)
app.include_router(get_all_router)
app.include_router(order_router)
app.include_router(people_router)
app.include_router(counterparty_router)
app.include_router(work_router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sibplc-kis3.ru", "http://localhost:3000", "http://localhost:80", "http://localhost",
                   'http://localhost:8000', 'http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175',
                   'http://localhost:5176'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) # type: ignore


@app.get("/")
def home():
    """Домашняя страница"""
    html_content = "<h2>FastAPI is the best backend framework</h2>"
    html_content += '<p>Интерактивная документация на <a href="/api/docs">  /api/docs  </a></p>'
    return HTMLResponse(content=html_content)


# для автоматического перезапуска приложения при изменении кода
if __name__ == "__main__":
    # Используйте эту команду для запуска с Uvicorn.
    # Uvicorn сам управляет циклом событий asyncio
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)  # Рекомендуемый запуск для разработки
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Для доступа извне localhost
