"""
Модуль для работы с базой данных через SQLAlchemy.
"""
# Для запуска в консоли:
# .venv\Scripts\python.exe D:\MyProgGit\KIS3_v2r2\backend\database.py

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import asyncio
from sqlalchemy import text
from colorama import init, Fore

# Инициализируем colorama
init(autoreset=True)

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем асинхронный session_maker
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


#  Зависимость для получения сессии базы данных
async def get_db():
    # Используем асинхронный менеджер контекста для создания сессии
    async with async_session_maker() as session:
        # Возвращаем сессию через yield
        yield session


async def test_connection():
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1"))
            print(Fore.GREEN + "Подключение к базе данных успешно!")  # Изменено на зелёный цвет
            print(f"Результат тестового запроса: {result.scalar()}")
            print("")
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        print("")


async def get_table_names(schema='public', print_results=True):
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


async def main():
    await test_connection()  # Запустить тест соединения
    await get_table_names()  # Запустить получение имен таблиц


if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции
