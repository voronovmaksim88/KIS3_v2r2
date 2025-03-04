# import_data.py
from KIS2.DjangoRestAPI import get_countries_set as get_countries_set_from_kis2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import async_session_maker
from models.models import *

from colorama import init, Fore
from sqlalchemy import create_engine, inspect
import os

# Инициализируем colorama
init(autoreset=True)

# Объявляем переменные
engine = None
inspector = None
Session = None  # Добавили переменную для сессии

try:
    # Попытаемся сначала импортировать настройки из config.py
    from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

    # Формируем строку подключения к PostgreSQL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(Fore.YELLOW + "Используем настройки подключения из config.py...")

    # Создание движка SQLAlchemy
    engine = create_engine(DATABASE_URL)

    # Создаем фабрику сессий
    Session = sessionmaker(bind=engine)

    # Получение инспектора
    inspector = inspect(engine)

    # Проверяем подключение
    with engine.connect() as connection:
        print(Fore.GREEN + "Соединение с базой данных успешно установлено.")

except ImportError:
    print(Fore.RED + "Ошибка: Не удалось импортировать настройки из config.py.")
    print(Fore.YELLOW + "Пытаюсь использовать alembic.ini...")

    try:
        from alembic.config import Config
        from alembic import command

        # Загрузка конфигурации Alembic
        alembic_cfg = Config("alembic.ini")

        # Получение текущей версии миграции
        command.current(alembic_cfg)

        # Получение URL базы данных из конфигурации Alembic
        DATABASE_URL = alembic_cfg.get_main_option("sqlalchemy.url")

        # Создание движка SQLAlchemy
        engine = create_engine(DATABASE_URL)

        # Создаем фабрику сессий
        Session = sessionmaker(bind=engine)

        # Получение инспектора
        inspector = inspect(engine)

        print(Fore.GREEN + "Соединение с базой данных через alembic.ini успешно установлено.")

    except Exception as e:
        print(Fore.RED + f"Ошибка: Не удалось создать подключение через alembic.ini. {e}")

except Exception as e:
    print(Fore.RED + f"Ошибка: Не удалось создать подключение к базе данных. {e}")
    print(Fore.YELLOW + "Пожалуйста, проверьте настройки подключения в config.py или .env файле.")


# Зависимость для получения сессии базы данных
async def get_db():
    async with async_session_maker() as session:
        yield session


# Функция для импорта стран, которая использует собственное соединение
def import_countries_from_kis2():
    # Убедимся, что сессия создана
    if Session is None:
        print(Fore.RED + "Ошибка: Не удалось создать сессию для базы данных.")
        return

    # Получаем множество стран из KIS2
    try:
        kis2_countries_set = get_countries_set_from_kis2()
    except Exception as e:
        print(Fore.RED + f"Ошибка при получении стран из KIS2: {e}")
        return

    # Открываем сессию
    with Session() as session:
        try:
            # Получаем существующие страны
            countries_query = session.query(Country.name).all()
            existing_countries = set(country[0] for country in countries_query)

            # Находим новые страны
            new_countries = kis2_countries_set - existing_countries

            if new_countries:
                # Подготавливаем данные для вставки
                insert_data = [{"name": country} for country in new_countries]

                # Добавляем новые страны
                session.bulk_insert_mappings(Country, insert_data)
                session.commit()
                print(Fore.GREEN + f"Добавлено {len(new_countries)} новых стран в базу данных КИС3(Postgres).")
            else:
                print(Fore.YELLOW + "Все страны уже существуют в базе данных.")
        except Exception as e:
            session.rollback()
            print(Fore.RED + f"Ошибка при импорте стран: {e}")


# Проверяем, что подключение к базе данных установлено, перед вызовом функции импорта
if engine is not None:
    try:
        # Вызываем функцию импорта при старте
        import_countries_from_kis2()
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта стран: {e}")
else:
    print(Fore.RED + "Импорт стран не выполнен: нет подключения к базе данных.")
