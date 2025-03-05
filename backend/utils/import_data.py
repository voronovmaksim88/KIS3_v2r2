# import_data.py
from KIS2.DjangoRestAPI import get_countries_set as get_countries_set_from_kis2
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import async_session_maker
from colorama import init, Fore
from models.models import Country

# Инициализируем colorama
init(autoreset=True)


def get_database_url_from_config():
    """Получить URL базы данных из config.py"""
    try:
        from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
        database_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(Fore.YELLOW + "Используем настройки подключения из config.py...")
        return database_url
    except ImportError:
        print(Fore.RED + "Ошибка: Не удалось импортировать настройки из config.py.")
        return None


def get_database_url_from_alembic():
    """Получить URL базы данных из alembic.ini"""
    try:
        from alembic.config import Config
        from alembic import command

        print(Fore.YELLOW + "Пытаюсь использовать alembic.ini...")
        alembic_cfg = Config("alembic.ini")
        command.current(alembic_cfg)
        database_url = alembic_cfg.get_main_option("sqlalchemy.url")
        return database_url
    except Exception as e:
        print(Fore.RED + f"Ошибка: Не удалось создать подключение через alembic.ini. {e}")
        return None


def setup_database_connection():
    """Настройка подключения к базе данных"""
    # Пытаемся получить URL базы данных сначала из config.py, затем из alembic.ini
    database_url = get_database_url_from_config()
    if database_url is None:
        database_url = get_database_url_from_alembic()

    if database_url is None:
        print(Fore.RED + "URL базы данных не определен. Невозможно установить соединение.")
        return None, None

    try:
        # Создание движка SQLAlchemy
        engine = create_engine(database_url)
        # Создаем фабрику сессий
        session = sessionmaker(bind=engine)
        # Проверяем подключение
        with engine.connect() as _:
            print(Fore.GREEN + "Соединение с базой данных успешно установлено.")
        return engine, session
    except Exception as e:
        print(Fore.RED + f"Ошибка: Не удалось создать подключение к базе данных. {e}")
        print(Fore.YELLOW + "Пожалуйста, проверьте настройки подключения.")
        return None, None


# Настраиваем подключение к базе данных
engine, Session = setup_database_connection()


# Зависимость для получения сессии базы данных
async def get_db():
    async with async_session_maker() as session:
        yield session


# Функция для импорта стран, которая использует собственное соединение
def import_countries_from_kis2():
    # Убедимся, что сессия создана
    if Session is None:
        print(Fore.RED + "Ошибка: Не удалось создать сессию для базы данных.")
        return 0  # Возвращаем 0, так как страны не были добавлены

    # Получаем множество стран из KIS2
    try:
        kis2_countries_set = get_countries_set_from_kis2()
    except Exception as e:
        print(Fore.RED + f"Ошибка при получении стран из KIS2: {e}")
        return 0  # Возвращаем 0, так как страны не были добавлены

    # Открываем сессию
    with Session() as session:
        try:
            # Получаем существующие страны
            countries_query = session.query(Country.name).all()
            existing_countries = set(country[0] for country in countries_query)

            # Находим новые страны
            new_countries = kis2_countries_set - existing_countries

            added_count = 0  # Счетчик добавленных стран

            if new_countries:
                # Подготавливаем данные для вставки
                insert_data = [{"name": country} for country in new_countries]

                # Добавляем новые страны
                session.bulk_insert_mappings(Country.__mapper__, insert_data)
                session.commit()
                added_count = len(new_countries)
                print(Fore.GREEN + f"Добавлено {added_count} новых стран в базу данных КИС3(Postgres).")
            else:
                print(Fore.YELLOW + "Все страны уже существуют в базе данных.")

            return added_count  # Возвращаем количество добавленных стран
        except Exception as e:
            session.rollback()
            print(Fore.RED + f"Ошибка при импорте стран: {e}")
            return 0  # В случае ошибки возвращаем 0


# Этот код выполняется только при прямом запуске файла, а не при импорте
if __name__ == "__main__":
    if engine is not None:
        try:
            # Вызываем функцию импорта при запуске скрипта напрямую
            import_countries_from_kis2()
        except Exception as e:
            print(Fore.RED + f"Ошибка при выполнении импорта стран: {e}")
    else:
        print(Fore.RED + "Импорт стран не выполнен: нет подключения к базе данных.")
