# Тут будем копировать данные из КИС2(БД SQlite3) в КИС3(БД PostgreSQL)
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import text as sql_text
from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as insert_pg
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert as pg_insert

from alembic.config import Config
from alembic import command
from tabulate import tabulate  # Для красивого вывода таблицы
from colorama import init, Fore
from KIS2.work_with_DB import get_set_countries as get_all_countries_set_from_sqlite3
from KIS2.work_with_DB import get_list_dict_manufacturers as get_all_manufacturers_from_sqlite3
from KIS2.work_with_DB import get_set_equipment_types as get_all_equipment_types_from_sqlite3
from KIS2.work_with_DB import get_set_cities as get_set_cities_from_sqlite3
from KIS2.work_with_DB import get_set_companies_form as get_set_companies_form_from_sqlite3
from KIS2.work_with_DB import get_list_dict_companies as get_list_dict_companies_from_sqlite3
from KIS2.work_with_DB import get_list_dict_person as get_list_dict_person_from_sqlite3
from KIS2.work_with_DB import get_list_dict_work as get_list_dict_work_from_sqlite3
from KIS2.work_with_DB import get_list_dict_orders as get_list_dict_orders_from_sqlite3
from KIS2.work_with_DB import get_list_dict_box_accounting as get_list_dict_box_accounting_from_sqlite3

from models.models import (Country, Manufacturer, EquipmentType, Currency, City, CounterpartyForm, Counterparty,
                           Person, Work, OrderStatus, Order, BoxAccounting)

import logging

# Инициализируем colorama
init(autoreset=True)

# Загрузка конфигурации Alembic
alembic_cfg = Config("alembic.ini")

# Объявляем переменные перед блоком try, чтобы к ним был доступ после выполнения try-except
engine = None
inspector = None

try:
    # Получение текущей версии миграции
    command.current(alembic_cfg)
    print(Fore.GREEN + "Соединение с базой данных успешно установлено.")

    # Получение URL базы данных из конфигурации Alembic
    db_url = alembic_cfg.get_main_option("sqlalchemy.url")

    # Создание движка SQLAlchemy
    engine = create_engine(db_url)

    # Получение инспектора
    inspector = inspect(engine)

except Exception as e:
    print(f"Ошибка: Не удалось создать инспектор базы данных. {e}")


def get_all_tables_name_from_postgre_sql():
    # Получение списка всех таблиц
    tables = inspector.get_table_names()

    if tables:
        print(Fore.LIGHTBLUE_EX + "Список таблиц в базе данных:")
        i = 1
        for table in tables:
            print(Fore.LIGHTBLUE_EX + f" {i}. {table}")
            i += 1
    else:
        print(Fore.RED + "Нет таблиц в базе данных.")
    print()


def show_table_country_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM countries"))
        columns = list(result.keys())
        data = result.fetchall()
        print("nСодержимое таблицы 'Country' в базе данных PostgreSQL:")
        print(tabulate(data, headers=columns, tablefmt='grid'))


def copy_table_country_from_sqlite_to_postgresql(countries_set):
    if not isinstance(countries_set, set):
        raise TypeError("Argument must be a set")

    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            # Получаем существующие страны из базы данных
            existing_countries = set(row[0] for row in connection.execute(sql_text("SELECT name FROM countries")))

            # Находим новые страны, которых еще нет в базе данных
            new_countries = countries_set - existing_countries

            if new_countries:
                # Подготавливаем данные для вставки
                insert_data = [{"name": country} for country in new_countries]

                # Выполняем вставку новых стран
                connection.execute(insert(Country), insert_data)  # type: ignore
                print(f"Добавлено {len(new_countries)} новых стран в базу данных.")
            else:
                print(Fore.GREEN + "Все страны уже существуют в базе данных.")


def show_table_manufacturers_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM manufacturers"))
        columns = list(result.keys())
        data = result.fetchall()
        print("nСодержимое таблицы 'Manufacturer' в базе данных PostgreSQL:")
        print(tabulate(data, headers=columns, tablefmt='grid'))


def copy_table_manufacturers_from_sqlite_to_postgresql(manufacturers_list_dict):
    # Это список словарей, каждый словарь хранит запись о производителе
    # Ключи: name-название, country-страна. Например, {'name':"Zentec", 'country':"Россия"}
    # Множество словарей создать в python нельзя
    if not isinstance(manufacturers_list_dict, list):
        raise TypeError("Argument must be a list")

    manufacturers_set = set()
    for manufacturers_dict in manufacturers_list_dict:
        manufacturers_set.add(manufacturers_dict['name'])
    print(manufacturers_set)

    with (engine.connect() as connection):
        # Начинаем транзакцию
        with connection.begin():

            # Формируем словарь стран из базы данных PostrgeSQL
            countries_dict = {}
            for row in connection.execute(sql_text("SELECT name, id FROM countries")):
                countries_dict[row[0]] = row[1]

            # Получаем существующие записи о производителях из базы данных PostrgeSQL
            existing_manufacturers = set(
                row[0] for row in connection.execute(sql_text("SELECT name FROM manufacturers")))

            # Формируем список новых производителей, которых еще нет в базе данных
            new_manufacturers_list = []
            for manufacturers_dict in manufacturers_list_dict:
                print(manufacturers_dict)
                if manufacturers_dict['name'] not in existing_manufacturers:
                    new_manufacturers_list.append(manufacturers_dict)
            print(new_manufacturers_list)

            if new_manufacturers_list:
                # Подготавливаем данные для вставки
                insert_data = [
                    {"name": manufacturer_dict['name'], "country_id": countries_dict[manufacturer_dict['country']]} for
                    manufacturer_dict in new_manufacturers_list]
                print('insert_data', insert_data)
                # Выполняем вставку новых производителей
                connection.execute(insert(Manufacturer), insert_data)  # type: ignore
                print(f"Добавлено {len(insert_data)} новых производителей в базу данных.")

            else:
                print(Fore.GREEN + "Все производители уже существуют в базе данных.")


def show_table_equipment_type_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM equipment_types"))
        columns = list(result.keys())
        data = result.fetchall()
        print("nСодержимое таблицы 'EquipmentType' в базе данных PostgreSQL:")
        print(tabulate(data, headers=columns, tablefmt='grid'))


def copy_table_equipment_type_from_sqlite_to_postgresql(equipment_type_set):
    if not isinstance(equipment_type_set, set):
        raise TypeError("Argument must be a set")

    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            # Получаем существующие типы оборудования из базы данных
            existing_type_set = set(row[0] for row in connection.execute(sql_text("SELECT name FROM equipment_types")))

            # Находим новые типы оборудования, которых еще нет в базе данных кис3
            new_equipment_type_set = equipment_type_set - existing_type_set

            if new_equipment_type_set:
                # Подготавливаем данные для вставки
                insert_data = [{"name": equipment_type} for equipment_type in new_equipment_type_set]

                # Выполняем вставку новых типов оборудования
                connection.execute(insert(EquipmentType), insert_data)  # type: ignore
                print(f"Добавлено {len(new_equipment_type_set)} новых типов оборудования в базу данных КИС3.")
            else:
                print(Fore.GREEN + "Все типы оборудования уже существуют в базе данных.")


def show_table_currency_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM currencies"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\nСодержимое таблицы 'Money' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def fill_in_table_currency_in_postgre_sql():
    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            insert_data = [{"name": 'RUB'}, {"name": 'USD'}, {"name": 'EUR'}]
            # Выполняем вставку новых валют
            try:
                connection.execute(insert(Currency), insert_data)  # type: ignore
                print(f"Добавлено {len(insert_data)} новых названия валют в базу данных PostgreSQL.")
            except Exception as err:
                print(Fore.RED + f"Ошибка: {err}")


def show_table_city_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM cities"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\n Содержимое таблицы 'City' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def get_set_cities_from_postgre_sql():
    with engine.connect() as connection:
        # Формируем словарь городов из базы данных PostrgeSQL
        cities_dict = {}
        for row in connection.execute(sql_text("SELECT name, id FROM cities")):
            cities_dict[row[0]] = row[1]
    return cities_dict


def copy_table_city_from_sqlite_to_postgresql(set_cities):
    if not isinstance(set_cities, set):
        raise TypeError("Argument must be a set")  # Проверка типа
    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            # Формируем словарь стран из базы данных PostrgeSQL
            countries_dict = {}
            for row in connection.execute(sql_text("SELECT name, id FROM countries")):
                countries_dict[row[0]] = row[1]

            # Получаем существующие города из базы данных
            existing_cities = set(row[0] for row in connection.execute(sql_text("SELECT name FROM cities")))

            # Находим новые города, которых еще нет в базе данных кис3
            new_cities = set_cities - existing_cities

            if new_cities:
                # Подготавливаем данные для вставки
                insert_data = [{"name": city, "country_id": countries_dict['Россия']} for city in new_cities]
                # Выполняем вставку новых городов, в КИС2 все города Российские
                connection.execute(insert(City), insert_data)  # type: ignore
                print(f"Добавлено {len(new_cities)} новых городов в базу данных КИС3.")
            else:
                print(Fore.GREEN + "Все города уже существуют в базе данных.")


def show_table_counterparty_form_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM counterparty_form"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\n Содержимое таблицы 'CompaniesForm' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def get_set_counterparty_form_from_postgre_sql():
    with engine.connect() as connection:
        # Формируем словарь типов компаний из базы данных PostrgeSQL
        companies_form_dict = {}
        for row in connection.execute(sql_text("SELECT name, id FROM counterparty_form")):
            companies_form_dict[row[0]] = row[1]
    return companies_form_dict


def copy_table_companies_form_from_sqlite_to_postgresql(set_companies_form):
    if not isinstance(set_companies_form, set):
        raise TypeError("Argument must be a set")

    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            # Получаем существующие типы компаний из базы данных
            existing_companies_form_set = set(
                row[0] for row in connection.execute(sql_text("SELECT name FROM counterparty_form")))

            # Находим новые типы компаний, которых еще нет в базе данных кис3
            new_companies_form_set = set_companies_form - existing_companies_form_set

            if new_companies_form_set:
                # Подготавливаем данные для вставки
                insert_data = [{"name": companies_form} for companies_form in new_companies_form_set]

                # Выполняем вставку новых типов компаний
                connection.execute(insert(CounterpartyForm), insert_data)  # type: ignore
                print(Fore.GREEN +
                      f"Добавлено {len(new_companies_form_set)} новых ОПФ(организационно правовых форм)"
                      f" в базу данных PostgreSQL.")
            else:
                print(Fore.GREEN + "Все ОПФ(организационно правовые формы)  уже существуют в базе данных PostgreSQL.")


def get_dict_counterparties_from_postgre_sql():
    """
    :return: Словарь контрагентов из базы данных PostrgeSQL
    в котором ключи это название контрагента, а значение это идентификатор(id)
    Пример:
    {"СИБПЛК": 1,
    "Вентавтоматика": 2,
    "Барион": 3}
    
    """
    with engine.connect() as connection:
        # Формируем словарь контрагентов из базы данных PostrgeSQL
        counterparties_dict = {}
        for row in connection.execute(sql_text("SELECT name, id FROM counterparty")):
            counterparties_dict[row[0]] = row[1]
    return counterparties_dict


def show_table_counterparties_in_postgre_sql():
    counterparties_dict = get_dict_counterparties_from_postgre_sql()

    if not counterparties_dict:
        print(Fore.RED + "Таблица 'Counterparties' в базе данных PostgreSQL пуста.")
        return
    else:
        with engine.connect() as connection:
            # Получаем полную информацию о контрагентах
            result = connection.execute(sql_text("""
                SELECT c.id, c.name, c.note, ci.name as city, cf.name as form
                FROM counterparty c
                LEFT JOIN cities ci ON c.city_id = ci.id
                LEFT JOIN counterparty_form cf ON c.form_id = cf.id
                ORDER BY c.id
            """))

            columns = list(result.keys())
            data = result.fetchall()

        print(Fore.LIGHTBLUE_EX + "\nСодержимое таблицы 'Counterparties' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))

        # Дополнительная информация о количестве контрагентов
        print(Fore.GREEN + f"\nОбщее количество контрагентов: {len(counterparties_dict)}")


def copy_table_counterparties_from_sqlite_to_postgresql(list_dict_companies):
    if not isinstance(list_dict_companies, list):
        raise TypeError("Argument must be a list")
    set_companies_from_sqlite = {companies['name'] for companies in list_dict_companies}

    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            # Получаем существующие типы компаний из базы данных
            existing_counterparties_set = set(
                row[0] for row in connection.execute(sql_text("SELECT name FROM counterparty")))

            # Находим новые типы компаний, которых еще нет в базе данных кис3
            new_counterparties_set = set_companies_from_sqlite - existing_counterparties_set
            new_counterparties_list_dict = []
            if new_counterparties_set:
                for company in list_dict_companies:
                    if company['name'] in new_counterparties_set:
                        new_counterparties_list_dict.append(company)

            if new_counterparties_list_dict:
                # Выполняем вставку новых типов компаний
                set_cities_from_postgre_sql = get_set_cities_from_postgre_sql()
                set_counterparty_form_from_postgre_sql = get_set_counterparty_form_from_postgre_sql()
                insert_data = []
                for new_counterparty_dict in new_counterparties_list_dict:
                    insert_data.append({'name': new_counterparty_dict['name'],
                                        'note': new_counterparty_dict['note'],
                                        'city_id': set_cities_from_postgre_sql[new_counterparty_dict['city']],
                                        'form_id': set_counterparty_form_from_postgre_sql[new_counterparty_dict['form']]
                                        })

                # Выполняем вставку новых типов компаний
                connection.execute(insert(Counterparty), insert_data)  # type: ignore
                print(Fore.GREEN +
                      f"Добавлено {len(new_counterparties_set)} новых контрагентов в базу данных PostgreSQL.")
            else:
                print(Fore.GREEN + "Все типы компаний  уже существуют в базе данных PostgreSQL.")


def show_table_people_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM people"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\n Содержимое таблицы 'Person' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def copy_table_people_from_sqlite_to_postgresql(list_dict_person):
    if not isinstance(list_dict_person, list):
        raise TypeError("Argument must be a list")

    # Получаем сопоставление компаний и их ID
    counterparty_map = get_dict_counterparties_from_postgre_sql()

    try:
        with engine.begin() as connection:
            # Получаем существующие записи о людях
            existing_people = connection.execute(
                select(Person.id, Person.surname, Person.name, Person.patronymic)
            ).fetchall()
            existing_keys = {
                f"{row.surname}{row.name}{row.patronymic}": row.id
                for row in existing_people
            }

            insert_data = []
            update_data = []

            for person in list_dict_person:
                key = f"{person['surname']}{person['name']}{person['patronymic']}"
                person_entry = {
                    'name': person['name'],
                    'surname': person['surname'],
                    'patronymic': person['patronymic'],
                    'phone': person.get('phone'),
                    'email': person.get('email'),
                    'counterparty_id': counterparty_map.get(person['company'])
                }

                if key in existing_keys:
                    person_entry['id'] = existing_keys[key]
                    update_data.append(person_entry)
                else:
                    insert_data.append(person_entry)

            # Вставка новых записей
            if insert_data:
                connection.execute(insert(Person), insert_data)
                print(Fore.GREEN + f"Добавлено {len(insert_data)} новых записей")
            else:
                print(Fore.GREEN + "Новых записей для добавления нет.")

            # Обновление существующих записей
            if update_data:
                stmt = pg_insert(Person).values(update_data)
                update_stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={
                        'phone': stmt.excluded.phone,
                        'email': stmt.excluded.email,
                        'counterparty_id': stmt.excluded.counterparty_id
                    }
                )
                result = connection.execute(update_stmt)
                print(Fore.GREEN + f"Обновлено {result.rowcount} существующих записей")
            else:
                print(Fore.GREEN + "Все существующие данные актуальны. Изменения не требуются.")
    except SQLAlchemyError as err:
        print(Fore.RED + f"Произошла ошибка при работе с базой данных: {err}")
        raise  # Повторно возбуждаем исключение после логирования
    except Exception as err:
        print(Fore.RED + f"Произошла непредвиденная ошибка: {err}")
        raise  # Повторно возбуждаем исключение после логирования


def show_table_work_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM works"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\n Содержимое таблицы 'Work' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def copy_table_work_from_sqlite_to_postgresql(list_dict_work):
    if not isinstance(list_dict_work, list):
        raise TypeError("Argument must be a list")
    set_work_from_sqlite = {work['name'] for work in list_dict_work}
    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            # Получаем существующие записи о видах работ по заказам из базы данных PostgreSQL
            existing_work_set = set(
                row[0] for row in
                connection.execute(sql_text("SELECT name FROM works")))
            # Находим новые записи о работах, которых еще нет в базе данных кис3
            new_work_set = set_work_from_sqlite - existing_work_set
            new_work_list_dict = []
            if new_work_set:
                for work in list_dict_work:
                    if work['name'] in new_work_set:
                        new_work_list_dict.append(work)

            if new_work_list_dict:
                # Выполняем добавление новых видов работ по заказам
                insert_data = []
                for work in new_work_list_dict:
                    insert_data.append({'name': work['name'],
                                        'description': work['description'],
                                        'active': True,
                                        })
                connection.execute(insert(Work), insert_data)
                print(
                    Fore.GREEN + f"Добавлено {len(new_work_list_dict)} новых видов работ по заказам"
                                 f" в базу данных PostgreSQL.")
            else:
                print(Fore.GREEN + "Все виды работ по заказам  уже записаны в базе данных PostgreSQL.")


def show_table_order_status_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM order_statuses"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\n Содержимое таблицы 'OrderStatus' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def fill_in_table_order_status_in_postgre_sql():
    with engine.connect() as connection:
        # Начинаем транзакцию
        with connection.begin():
            insert_data = [{"name": 'Не определён'},
                           {"name": 'На согласовании'},
                           {"name": 'В работе'},
                           {"name": 'Просрочено'},
                           {"name": 'Выполнено в срок'},
                           {"name": 'Выполнено НЕ в срок'},
                           {"name": 'Не согласовано'},
                           {"name": 'На паузе'}]
            # Выполняем вставку новых статусов заказов
            try:
                connection.execute(insert(OrderStatus), insert_data)  # type: ignore
                print(Fore.GREEN + f"Добавлено {len(insert_data)} новых статусов заказов в базу данных PostgreSQL.")
            except Exception as err:
                print(Fore.RED + f"Ошибка: {err}")


def get_dict_order_status_from_postgre_sql():
    with engine.connect() as connection:
        # Формируем словарь контрагентов из базы данных PostrgeSQL
        dict_order_status = dict()
        for row in connection.execute(sql_text("SELECT name, id FROM order_statuses")):
            dict_order_status[row[0]] = row[1]
    return dict_order_status


def show_table_orders_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM orders"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\n Содержимое таблицы 'Orders' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def copy_table_orders_from_sqlite_to_postgresql(list_dict_orders):
    if not isinstance(list_dict_orders, list):
        raise TypeError("Argument must be a list")

    dict_counterparties_from_postgre_sql = get_dict_counterparties_from_postgre_sql()
    dict_order_status_from_postgre_sql = get_dict_order_status_from_postgre_sql()
    with engine.connect() as connection:
        try:
            with connection.begin():
                # Получаем существующие записи о заказах из базы данных PostgreSQL
                existing_orders = connection.execute(
                    select(Order.serial)
                ).fetchall()

                existing_order_set = {row.serial for row in existing_orders}

                insert_data = []
                update_data = []

                for order_in_sqlite in list_dict_orders:
                    key = order_in_sqlite['serial']
                    order_data = {
                        'serial': order_in_sqlite['serial'],
                        'name': order_in_sqlite['name'],
                        'customer_id': dict_counterparties_from_postgre_sql[order_in_sqlite['customer']],
                        'status_id': dict_order_status_from_postgre_sql[order_in_sqlite['status']],
                    }
                    if key in existing_order_set:
                        order_data['serial'] = key
                        update_data.append(order_data)
                    else:
                        insert_data.append(order_data)

                if insert_data:
                    connection.execute(insert(Order), insert_data)
                    print(Fore.GREEN + f"Добавлено {len(insert_data)} новых записей о заказах")
                else:  # Если нет новых записей
                    print(Fore.GREEN + "Новых записей для добавления нет.")

                if update_data:
                    stmt = insert_pg(Order).values(update_data)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['serial'],
                        set_={
                            'name': stmt.excluded.name,
                            'customer_id': stmt.excluded.customer_id
                        }
                    )
                    result = connection.execute(stmt)
                    print(Fore.GREEN + f"Обновлено {result.rowcount} существующих записей")
                else:  # Если нет новых записей
                    print(Fore.GREEN + "")
        except SQLAlchemyError as err:
            print(Fore.RED + f"Произошла ошибка при работе с базой данных: {err}")
            connection.rollback()
        except Exception as err:
            print(Fore.RED + f"Произошла непредвиденная ошибка: {err}")
            connection.rollback()


def show_table_box_accounting_in_postgre_sql():
    with engine.connect() as connection:
        result = connection.execute(sql_text("SELECT * FROM box_accounting"))
        columns = list(result.keys())
        data = result.fetchall()
        print(Fore.LIGHTBLUE_EX + "\n Содержимое таблицы 'box_accounting' в базе данных PostgreSQL:")
        print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))


def get_dict_people_from_postgre_sql():
    with engine.connect() as connection:
        # Формируем словарь людей из базы данных PostrgeSQL
        dict_people = dict()
        for row in connection.execute(sql_text("SELECT id, surname, name, patronymic  FROM people")):
            dict_people[row[1] + row[2] + row[3]] = row[0]
    return dict_people


def copy_table_box_accounting_in_postgre_sql(list_dict_box_accounting):
    if not isinstance(list_dict_box_accounting, list):
        raise TypeError("Argument must be a list")

    people_dict_from_postgre_sql = get_dict_people_from_postgre_sql()
    logging.info(f"Получен словарь людей: {people_dict_from_postgre_sql}")

    with engine.connect() as connection:
        try:
            with connection.begin():
                existing_box_accounting = connection.execute(select(BoxAccounting.serial_num)).fetchall()
                existing_box_accounting_set = {row.serial_num for row in existing_box_accounting}

                insert_data = []
                update_data = []
                for box_accounting in list_dict_box_accounting:
                    key = box_accounting['serial_num']
                    box_accounting_data = {
                        'serial_num': box_accounting['serial_num'],
                        'name': box_accounting['name'],
                        'order_id': box_accounting.get('order_id'),
                        'scheme_developer_id': people_dict_from_postgre_sql.get(box_accounting.get('scheme_developer')),
                        'assembler_id': people_dict_from_postgre_sql.get(box_accounting.get('assembler')),
                        'programmer_id': people_dict_from_postgre_sql.get(box_accounting.get('programmer')),
                        'tester_id': people_dict_from_postgre_sql.get(box_accounting.get('tester'))
                    }
                    if key in existing_box_accounting_set:
                        update_data.append(box_accounting_data)
                    else:
                        insert_data.append(box_accounting_data)

                if insert_data:
                    connection.execute(insert(BoxAccounting), insert_data)
                    print(Fore.GREEN + f"Добавлено {len(insert_data)} новых записей о серийных номерах шкафов")
                    logging.info(f"Добавлено {len(insert_data)} новых записей")
                else:
                    print(Fore.GREEN + "Новых записей для добавления нет.")
                    logging.info("Новых записей для добавления нет.")

                if update_data:
                    stmt = insert_pg(BoxAccounting).values(update_data)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['serial_num'],
                        set_={
                            'name': stmt.excluded.name,
                            'order_id': stmt.excluded.order_id,
                            'scheme_developer_id': stmt.excluded.scheme_developer_id,
                            'assembler_id': stmt.excluded.assembler_id,
                            'programmer_id': stmt.excluded.programmer_id,
                            'tester_id': stmt.excluded.tester_id
                        }
                    )
                    result = connection.execute(stmt)
                    print(Fore.GREEN + f"Обновлено {result.rowcount} существующих записей")
                    logging.info(f"Обновлено {result.rowcount} существующих записей")
                else:
                    print(Fore.GREEN + "Нет записей для обновления.")
                    logging.info("Нет записей для обновления.")
        except SQLAlchemyError as err:
            print(Fore.RED + f"Произошла ошибка при работе с базой данных: {err}")
            logging.error(f"Ошибка SQLAlchemy: {err}")
            connection.rollback()
        except Exception as err:
            print(Fore.RED + f"Произошла непредвиденная ошибка: {err}")
            logging.error(f"Непредвиденная ошибка: {err}")
            connection.rollback()
        else:
            print(Fore.GREEN + "Операция успешно завершена.")
            logging.info("Операция успешно завершена.")


answer1 = ""
answer2 = ""
while answer1 != "e":
    print("")
    print("Change action:")
    print("e - exit")
    print("1 - show ")
    print("2 - copy")
    answer2 = ""
    answer1 = input()

    if answer1 == "e":
        break

    elif answer1 == "1":
        while answer2 != "e":
            print("")
            print("What show ?")
            print("e - exit")
            print("1 - show all tables name in PostgreSQL")
            print("2 - show table 'Country' in PostgreSQL")
            print("4 - show table 'Manufacturers' in PostgreSQL")
            print("6 - show table 'EquipmentType' in PostgreSQL")
            print("8 - show table 'Currency' in PostgreSQL")
            print("10 - show table 'City' in PostgreSQL")
            print("12 - show table 'CounterpartyForm' in PostgreSQL")
            print("14 - show table 'Counterparties' in PostgreSQL")
            print("16 - show table 'Person' in PostgreSQL")
            print("18 - show table 'Work' in PostgreSQL")
            print("20 - show table 'OrderStatus' in PostgreSQL")
            print("22 - show table 'Order' in PostgreSQL")
            print("24 - show table box_accounting in PostgreSQL")

            answer2 = input()

            if answer2 == "0":
                break
            elif answer2 == "1":
                get_all_tables_name_from_postgre_sql()
            elif answer2 == "2":
                show_table_country_in_postgre_sql()
            elif answer2 == "4":
                show_table_manufacturers_in_postgre_sql()
            elif answer2 == "6":
                show_table_equipment_type_in_postgre_sql()
            elif answer2 == "8":
                show_table_currency_in_postgre_sql()
            elif answer2 == "10":
                show_table_city_in_postgre_sql()
            elif answer2 == "12":
                show_table_counterparty_form_in_postgre_sql()
            elif answer2 == "14":
                show_table_counterparties_in_postgre_sql()
            elif answer2 == "16":
                show_table_people_in_postgre_sql()
            elif answer2 == "18":
                show_table_work_in_postgre_sql()
            elif answer2 == "20":
                show_table_order_status_in_postgre_sql()
            elif answer2 == "22":
                show_table_orders_in_postgre_sql()
            elif answer2 == "24":
                show_table_box_accounting_in_postgre_sql()
            else:
                print(Fore.RED + "Please enter a valid number.")
            print("")

    elif answer1 == "2":
        while answer2 != "e":
            print("")
            print("What copy ?")
            print("e - exit")
            print("3 - copy table 'Country' from sqlite to PostgreSQL")
            print("5 - copy table 'Manufacturers' from sqlite to PostgreSQL")
            print("7 - copy table 'EquipmentType' from sqlite to PostgreSQL")
            print("9 - fill in the table 'Currency'")
            print("11 - copy table 'City' from SQlite to PostgreSQL")
            print("13 - copy table 'CounterpartyForm' from SQlite to PostgreSQL")
            print("15 - copy table 'Counterparties' from SQlite to PostgreSQL")
            print("17 - copy table 'Person' from SQlite to PostgreSQL")
            print("19 - copy table 'Work' from SQlite to PostgreSQL")
            print("21 - fill table 'OrderStatus' from SQlite to PostgreSQL")
            print("23 - copy table 'Order' from SQlite to PostgreSQL")
            print("25 - copy table 'box_accounting' from SQlite to PostgreSQL")

            answer2 = input()

            if answer2 == "0":
                break
            elif answer2 == "2":
                show_table_country_in_postgre_sql()
            elif answer2 == "3":
                copy_table_country_from_sqlite_to_postgresql(get_all_countries_set_from_sqlite3())
            elif answer2 == "5":
                copy_table_manufacturers_from_sqlite_to_postgresql(get_all_manufacturers_from_sqlite3())
            elif answer2 == "7":
                copy_table_equipment_type_from_sqlite_to_postgresql(get_all_equipment_types_from_sqlite3())
            elif answer2 == "9":
                fill_in_table_currency_in_postgre_sql()
            elif answer2 == "11":
                copy_table_city_from_sqlite_to_postgresql(get_set_cities_from_sqlite3())
            elif answer2 == "13":
                copy_table_companies_form_from_sqlite_to_postgresql(get_set_companies_form_from_sqlite3())
            elif answer2 == "15":
                copy_table_counterparties_from_sqlite_to_postgresql(get_list_dict_companies_from_sqlite3())
            elif answer2 == "17":
                copy_table_people_from_sqlite_to_postgresql(get_list_dict_person_from_sqlite3())
            elif answer2 == "19":
                copy_table_work_from_sqlite_to_postgresql(get_list_dict_work_from_sqlite3())
            elif answer2 == "21":
                fill_in_table_order_status_in_postgre_sql()
            elif answer2 == "23":
                copy_table_orders_from_sqlite_to_postgresql(get_list_dict_orders_from_sqlite3())
            elif answer2 == "25":
                copy_table_box_accounting_in_postgre_sql(get_list_dict_box_accounting_from_sqlite3())
            else:
                print(Fore.RED + "Please enter a valid number.")
            print("")

    else:
        print(Fore.RED + "Please enter a valid number.")
