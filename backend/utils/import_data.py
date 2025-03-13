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
from models.models import Country, Manufacturer  # noqa: E402

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
                    print(Fore.YELLOW + "Все страны уже существуют в базе данных КИС2.")

                return added_count
            except Exception as db_error:  # Изменено имя переменной
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте стран: {db_error}")
                return 0
    except Exception as e1:
        print(Fore.RED + f"Ошибка при выполнении импорта стран: {e1}")
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
    except Exception as e2:
        print(Fore.RED + f"Ошибка при получении списка существующих стран: {e2}")
        return set()


def import_manufacturers_from_kis2() -> int:
    """
    Импортировать производителей из КИС2 в базу данных КИС3.

    Returns:
        int: Количество добавленных производителей.
    """
    try:
        # Получаем список словарей производителей из KIS2
        kis2_manufacturers_list = create_def_list_dict_manufacturers(debug=False)
        if not kis2_manufacturers_list:
            print(Fore.YELLOW + "Не удалось получить производителей из КИС2 или список пуст.")
            return 0

        print(Fore.CYAN + f"Получено {len(kis2_manufacturers_list)} производителей из КИС2.")

        # Открываем сессию
        with SyncSession() as session:
            try:
                # Получаем существующих производителей
                manufacturers_query = session.query(Manufacturer.name).all()
                existing_manufacturers = set(manufacturer[0] for manufacturer in manufacturers_query)

                # Получаем словарь стран {название: id}
                countries_query = session.query(Country.id, Country.name).all()
                countries_dict = {country_name: country_id for country_id, country_name in countries_query}

                # Проверяем наличие всех стран и создаем отсутствующие
                unique_countries = set(item['country'] for item in kis2_manufacturers_list)
                missing_countries = unique_countries - set(countries_dict.keys())

                if missing_countries:
                    print(Fore.YELLOW + f"Обнаружено {len(missing_countries)} отсутствующих стран. Добавление...")
                    for country_name in missing_countries:
                        new_country = Country(name=country_name)
                        session.add(new_country)

                    session.commit()

                    # Обновляем словарь стран после добавления новых
                    countries_query = session.query(Country.id, Country.name).all()
                    countries_dict = {country_name: country_id for country_id, country_name in countries_query}
                    print(Fore.GREEN + f"Добавлено {len(missing_countries)} стран.")

                # Подготавливаем данные для вставки производителей
                added_count = 0
                for manufacturer_data in kis2_manufacturers_list:
                    manufacturer_name = manufacturer_data['name']
                    country_name = manufacturer_data['country']

                    # Пропускаем, если производитель уже существует
                    if manufacturer_name in existing_manufacturers:
                        continue

                    # Получаем ID страны
                    country_id = countries_dict.get(country_name)
                    if not country_id:
                        print(Fore.RED + f"Не удалось найти ID для страны '{country_name}'."
                                         f" Пропуск производителя '{manufacturer_name}'.")
                        continue

                    # Создаем нового производителя
                    new_manufacturer = Manufacturer(
                        name=manufacturer_name,
                        country_id=country_id
                    )
                    session.add(new_manufacturer)
                    added_count += 1

                # Сохраняем изменения
                if added_count > 0:
                    session.commit()
                    print(Fore.GREEN + f"Добавлено {added_count} новых производителей в базу данных КИС3(Postgres).")
                else:
                    print(Fore.YELLOW + "Все производители уже существуют в базе данных КИС3.")

                return added_count

            except Exception as e3:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте производителей: {e3}")
                return 0
    except Exception as e4:
        print(Fore.RED + f"Ошибка при выполнении импорта производителей: {e4}")
        return 0


def import_equipment_type_from_kis2() -> int:
    """
    Импортировать типы оборудования из КИС2 в базу данных КИС3.

    Returns:
        int: Количество добавленных типов оборудования.
    """
    try:
        # Импортируем функцию получения типов оборудования из КИС2
        from kis2.DjangoRestAPI import create_equipment_type_set_from_kis2
        from models.models import EquipmentType  # Предполагается, что такая модель существует

        # Получаем множество типов оборудования из KIS2
        kis2_equipment_types_set = create_equipment_type_set_from_kis2(debug=False)
        if not kis2_equipment_types_set:
            print(Fore.YELLOW + "Не удалось получить типы оборудования из КИС2 или список пуст.")
            return 0

        print(Fore.CYAN + f"Получено {len(kis2_equipment_types_set)} типов оборудования из КИС2.")

        # Открываем сессию
        with SyncSession() as session:
            try:
                # Получаем существующие типы оборудования
                equipment_types_query = session.query(EquipmentType.name).all()
                existing_equipment_types = set(equipment_type[0] for equipment_type in equipment_types_query)

                # Находим новые типы оборудования
                new_equipment_types = kis2_equipment_types_set - existing_equipment_types

                added_count = 0

                if new_equipment_types:
                    # Подготавливаем данные для вставки
                    insert_data = [{"name": equipment_type} for equipment_type in new_equipment_types]

                    # Добавляем новые типы оборудования
                    session.bulk_insert_mappings(EquipmentType.__mapper__, insert_data)
                    session.commit()
                    added_count = len(new_equipment_types)
                    print(Fore.GREEN + f"Добавлено {added_count} новых типов оборудования в базу данных КИС3(Postgres).")
                else:
                    print(Fore.YELLOW + "Все типы оборудования уже существуют в базе данных КИС3.")

                return added_count
            except Exception as db_error:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте типов оборудования: {db_error}")
                return 0
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта типов оборудования: {e}")
        return 0


# Этот код выполняется только при прямом запуске файла, а не при импорте
if __name__ == "__main__":
    answer = ""
    while answer != "e":
        print("")
        print("Change action:")
        print("e - exit")
        print("1 - copy countries from KIS2 ")
        print("2 - copy manufacturers from KIS2")
        print("3 - copy equipment types from KIS2")  # Добавлена новая опция
        answer = input()

        if answer == "1":
            if test_sync_connection():
                try:
                    print(Fore.CYAN + "=== Импорт стран из КИС2 ===")
                    imported_count = import_countries_from_kis2()
                    print(Fore.GREEN + f"Импортировано стран: {imported_count}")
                except Exception as e:
                    print(Fore.RED + f"Ошибка при выполнении операций с данными: {e}")
            else:
                print(Fore.RED + "Операции с данными не выполнены: нет подключения к базе данных.")

        elif answer == "2":
            if test_sync_connection():
                try:
                    print(Fore.CYAN + "=== Импорт производителей из КИС2 ===")
                    imported_count = import_manufacturers_from_kis2()
                    print(Fore.GREEN + f"Импортировано производителей: {imported_count}")
                except Exception as e:
                    print(Fore.RED + f"Ошибка при выполнении импорта производителей: {e}")
            else:
                print(Fore.RED + "Операции с данными не выполнены: нет подключения к базе данных.")

        elif answer == "3":  # Добавлен новый вариант
            if test_sync_connection():
                try:
                    print(Fore.CYAN + "=== Импорт типов оборудования из КИС2 ===")
                    imported_count = import_equipment_type_from_kis2()
                    print(Fore.GREEN + f"Импортировано типов оборудования: {imported_count}")
                except Exception as e:
                    print(Fore.RED + f"Ошибка при выполнении импорта типов оборудования: {e}")
            else:
                print(Fore.RED + "Операции с данными не выполнены: нет подключения к базе данных.")

        elif answer != "e":
            break

    print("Goodbye!")