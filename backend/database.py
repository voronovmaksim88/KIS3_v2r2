"""
Модуль для работы с базой данных через SQLAlchemy.
Поддерживает как синхронное, так и асинхронное подключение.
"""
# Для запуска в консоли:
# .venv\Scripts\python.exe D:\MyProgGit\KIS3_v2r2\backend\database.py

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import asyncio
from colorama import init, Fore
from typing import List

# Инициализируем colorama
init(autoreset=True)

# Формируем URL для подключения к базе данных
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL_SYNC = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем асинхронный движок и сессию
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Создаем синхронный движок и сессию
sync_engine = create_engine(DATABASE_URL_SYNC, echo=False)
SyncSession = sessionmaker(bind=sync_engine)


# Зависимость для получения асинхронной сессии базы данных (для FastAPI)
async def get_async_db():
    """Получить асинхронную сессию для работы с базой данных (для FastAPI)"""
    async with async_session_maker() as session:
        yield session


# Получение синхронной сессии (для обычных Python-скриптов)
def get_sync_db():
    """Получить синхронную сессию для работы с базой данных"""
    return SyncSession()


# Асинхронные методы работы с БД
async def test_connection():
    """Проверка подключения к базе данных (асинхронно)"""
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1"))
            print(Fore.GREEN + "Асинхронное подключение к базе данных успешно!")
            print(f"Результат тестового запроса: {result.scalar()}")
            print("")
            return True
    except Exception as e:
        print(Fore.RED + f"Ошибка при асинхронном подключении к базе данных: {e}")
        print("")
        return False


async def get_table_names(schema='public', print_results=True) -> List[str]:
    """Получить список таблиц в указанной схеме (асинхронно)"""
    try:
        async with async_session_maker() as session:
            # noinspection SqlResolve
            result = await session.execute(
                text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = :schema"),
                {"schema": schema}
            )
            tables = result.scalars().all()

            if print_results:
                print(f"\n{Fore.CYAN}Имена таблиц в схеме {schema}:{Fore.RESET}")
                for i, table in enumerate(tables, 1):
                    print(f"{i}. {table}")

            return tables
    except Exception as e:
        print(f"{Fore.RED}Ошибка при получении имен таблиц: {e}{Fore.RESET}")
        return []


# Синхронные методы работы с БД
def test_sync_connection() -> bool:
    """Проверка подключения к базе данных (синхронно)"""
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(Fore.GREEN + "Синхронное подключение к базе данных успешно установлено.")
            print(f"Результат тестового запроса: {result}")
            print("")
            return True
    except Exception as e:
        print(Fore.RED + f"Ошибка при синхронном подключении к базе данных: {e}")
        print(Fore.YELLOW + "Пожалуйста, проверьте настройки подключения.")
        print("")
        return False


def get_sync_table_names(schema='public', print_results=True) -> List[str]:
    """Получить список таблиц в указанной схеме (синхронно)"""
    try:
        with SyncSession() as session:
            # noinspection SqlResolve
            result = session.execute(
                text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = :schema"),
                {"schema": schema}
            )
            tables = [row[0] for row in result]

            if print_results:
                print(f"\n{Fore.CYAN}Имена таблиц в схеме {schema} (синхронно):{Fore.RESET}")
                for i, table in enumerate(tables, 1):
                    print(f"{i}. {table}")

            return tables
    except Exception as e:
        print(f"{Fore.RED}Ошибка при получении имен таблиц (синхронно): {e}{Fore.RESET}")
        return []


# Асинхронная основная функция
async def async_main():
    """Асинхронная основная функция для демонстрации работы модуля"""
    print(Fore.CYAN + "=== Тестирование АСИНХРОННЫХ функций работы с БД ===")
    await test_connection()
    await get_table_names()


# Основная функция с поддержкой как асинхронных, так и синхронных операций
def main():
    """Основная функция для демонстрации работы модуля"""
    print(Fore.CYAN + "=== Тестирование СИНХРОННЫХ функций работы с БД ===")
    if test_sync_connection():
        get_sync_table_names()

    # Асинхронная часть
    print(Fore.CYAN + "\n=== Запуск асинхронных функций ===")
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
