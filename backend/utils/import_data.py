# utils/import_data.py
"""
Модуль импорта данных из КИС2(БД SQlite3) в КИС3(БД PostgreSQL).
Получение данных из КИС2(БД SQlite3) реализовано через Django Rest API.
"""
import sys
import os
from colorama import init, Fore
from typing import Set

# Добавляем родительскую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорты, требующие модификации sys.path
from kis2.DjangoRestAPI import create_countries_set_from_kis2, create_def_list_dict_manufacturers  # noqa: E402
from database import SyncSession, test_sync_connection  # noqa: E402
from models.models import Country  # noqa: E402

# Инициализируем colorama
init(autoreset=True)


def import_countries_from_kis2() -> int:
    """
    Импортировать страны из КИС2 в базу данных.
    
    Returns:
        int: Количество добавленных стран.
    """
    try:
        # Получаем множество стран из KIS2
        kis2_countries_set = create_countries_set_from_kis2()
        if not kis2_countries_set:
            print(Fore.YELLOW + "Не удалось получить страны из KIS2 или список пуст.")
            return 0

        # Открываем сессию
        with SyncSession() as session:
            try:
                # Получаем существующие страны
                countries_query = session.query(Country.name).all()
                existing_countries = set(country[0] for country in countries_query)

                # Находим новые страны
                new_countries = kis2_countries_set - existing_countries

                added_count = 0

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

                return added_count
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте стран: {e}")
                return 0
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта стран: {e}")
        return 0


# Функция для получения множества существующих стран в КИС3
def get_existing_countries_set() -> Set[str]:
    """
    Получить множество названий стран, уже существующих в базе данных КИС3.
    
    Returns:
        Set[str]: Множество названий стран.
    """
    try:
        with SyncSession() as session:
            countries_query = session.query(Country.name).all()
            return set(country[0] for country in countries_query)
    except Exception as e:
        print(Fore.RED + f"Ошибка при получении списка существующих стран: {e}")
        return set()


def import_manufacturers_from_kis2() -> int:
    """
    Для импорта производителей из КИС2 в КИС3.

    Returns:
        int: Количество добавленных производителей.
    """
    print("В разработке")
    kis2_list_dict_manufacturers = create_def_list_dict_manufacturers()
    print(kis2_list_dict_manufacturers)
    return 0


# Этот код выполняется только при прямом запуске файла, а не при импорте
if __name__ == "__main__":
    print(Fore.CYAN + "=== Проверка подключения к базе данных КИС3(Postgres) ===")

    # if test_sync_connection():
    #     try:
    #         print(Fore.CYAN + "=== Импорт стран из КИС2 ===")
    #         imported_count = import_countries_from_kis2()
    #         print(Fore.GREEN + f"Импортировано стран: {imported_count}")
    #
    #         # Демонстрация получения существующих стран
    #         print(Fore.CYAN + "\n=== Список существующих стран в КИС3 ===")
    #         existing_countries = get_existing_countries_set()
    #         print(f"Всего стран в базе: {len(existing_countries)}")
    #         if len(existing_countries) > 0:
    #             print("Первые 5 стран:")
    #             for country in list(existing_countries)[:5]:
    #                 print(f"  - {country}")
    #             if len(existing_countries) > 5:
    #                 print(f"  ...и еще {len(existing_countries) - 5} стран")
    #     except Exception as e:
    #         print(Fore.RED + f"Ошибка при выполнении операций с данными: {e}")
    # else:
    #     print(Fore.RED + "Операции с данными не выполнены: нет подключения к базе данных.")

    if test_sync_connection():
        try:
            print(Fore.CYAN + "=== Импорт производителей из КИС2 ===")
            imported_count = import_manufacturers_from_kis2()
            print(Fore.GREEN + f"Импортировано производителей: {imported_count}")
        except Exception as e:
            print(Fore.RED + f"Ошибка при выполнении импорта производителей: {e}")
    else:
        print(Fore.RED + "Операции с данными не выполнены: нет подключения к базе данных.")
