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


async def get_table_names():
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.scalars().all()  # Извлекаем имена таблиц
            print("Имена таблиц в базе данных:")
            for table in tables:
                print(table)
    except Exception as e:
        print(f"Ошибка при получении имен таблиц: {e}")


async def main():
    await test_connection()  # Запустить тест соединения
    await get_table_names()  # Запустить получение имен таблиц


if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции
