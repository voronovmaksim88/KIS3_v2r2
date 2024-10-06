# Тут будем копировать данные из КИС2(БД SQlite3) в КИС3(БД PostgreSQL)
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import text as sql_text
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as insert_pg
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import select
# from sqlalchemy import func

from alembic.config import Config
from alembic import command
from tabulate import tabulate  # Для красивого вывода таблицы
from colorama import init, Fore

import functools

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
from KIS2.work_with_DB import get_list_dict_order_comment as get_list_dict_order_comment_from_sqlite3

from models.models import (Country, Manufacturer, EquipmentType, Currency, City, CounterpartyForm, Counterparty,
                           Person, Work, OrderStatus, Order, BoxAccounting, OrderComment)

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
        for i, table in enumerate(tables, 1):
            print(Fore.LIGHTBLUE_EX + f" {i}. {table}")
    else:
        print(Fore.RED + "Нет таблиц в базе данных.")
    print()


def database_operation(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], list):
            raise TypeError("Первый аргумент должен быть списком")

        with engine.connect() as connection:
            try:
                with connection.begin():
                    result = func(*args, connection=connection, **kwargs)
                print(Fore.GREEN + "Операция успешно завершена.")
                logging.info("Операция успешно завершена.")
                return result
            except SQLAlchemyError as err:
                print(Fore.RED + f"Произошла ошибка при работе с базой данных: {err}")
                logging.error(f"Ошибка SQLAlchemy: {err}")
                connection.rollback()
            except Exception as err:
                print(Fore.RED + f"Произошла непредвиденная ошибка: {err}")
                logging.error(f"Непредвиденная ошибка: {err}")
                connection.rollback()

    return wrapper


def show_table_in_postgre_sql(table_name: str):
    with engine.connect() as connection:
        try:
            # Используем форматирование строки для имени таблицы
            # Это безопасно, так как мы не принимаем имя таблицы от пользователя напрямую
            query = sql_text(f"SELECT * FROM {table_name}")
            result = connection.execute(query)

            columns = list(result.keys())
            data = result.fetchall()

            if data:
                print(Fore.LIGHTBLUE_EX + f"\nСодержимое таблицы '{table_name}' в базе данных PostgreSQL:")
                print(Fore.LIGHTBLUE_EX + tabulate(data, headers=columns, tablefmt='grid'))
            else:
                print(Fore.YELLOW + f"\nТаблица '{table_name}' пуста.")
        except SQLAlchemyError as e1:
            print(Fore.RED + f"\nОшибка SQL при попытке отобразить таблицу '{table_name}': {str(e1)}")
        except Exception as e1:
            print(Fore.RED + f"\nНепредвиденная ошибка при попытке отобразить таблицу '{table_name}': {str(e1)}")


@database_operation
def copy_table_country_from_sqlite_to_postgresql(countries_list, connection):
    countries_set = set(countries_list)

    # Получаем существующие страны из базы данных
    existing_countries = set(connection.execute(select(Country.name)).scalars().all())

    # Находим новые страны, которых еще нет в базе данных
    new_countries = countries_set - existing_countries

    if new_countries:
        # Подготавливаем данные для вставки
        insert_data = [{"name": country} for country in new_countries]

        # Выполняем вставку новых стран
        stmt = pg_insert(Country).values(insert_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        result = connection.execute(stmt)
        print(f"Добавлено {result.rowcount} новых стран в базу данных.")
    else:
        print(Fore.GREEN + "Все страны уже существуют в базе данных.")


@database_operation
def copy_table_manufacturers_from_sqlite_to_postgresql(manufacturers_list_dict, connection):
    # Формируем словарь стран из базы данных PostgreSQL
    countries_dict = dict(connection.execute(select(Country.name, Country.id)).fetchall())

    # Получаем существующие записи о производителях из базы данных PostgreSQL
    existing_manufacturers = set(connection.execute(select(Manufacturer.name)).scalars().all())

    # Формируем список новых производителей, которых еще нет в базе данных
    new_manufacturers_list = [
        manufacturer for manufacturer in manufacturers_list_dict
        if manufacturer['name'] not in existing_manufacturers
    ]
    print("Новые производители:", new_manufacturers_list)

    if new_manufacturers_list:
        # Подготавливаем данные для вставки
        insert_data = [
            {
                "name": manufacturer['name'],
                "country_id": countries_dict[manufacturer['country']]
            }
            for manufacturer in new_manufacturers_list
        ]
        print('Данные для вставки:', insert_data)

        # Выполняем вставку новых производителей
        stmt = pg_insert(Manufacturer).values(insert_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        result = connection.execute(stmt)
        print(f"Добавлено {result.rowcount} новых производителей в базу данных.")
    else:
        print(Fore.GREEN + "Все производители уже существуют в базе данных.")


@database_operation
def copy_table_equipment_type_from_sqlite_to_postgresql(equipment_type_list, connection):
    equipment_type_set = set(equipment_type_list)

    # Получаем существующие типы оборудования из базы данных
    existing_type_set = set(connection.execute(select(EquipmentType.name)).scalars().all())

    # Находим новые типы оборудования, которых еще нет в базе данных КИС3
    new_equipment_type_set = equipment_type_set - existing_type_set

    if new_equipment_type_set:
        # Подготавливаем данные для вставки
        insert_data = [{"name": equipment_type} for equipment_type in new_equipment_type_set]

        # Выполняем вставку новых типов оборудования
        stmt = pg_insert(EquipmentType).values(insert_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        result = connection.execute(stmt)
        print(f"Добавлено {result.rowcount} новых типов оборудования в базу данных КИС3.")
    else:
        print(Fore.GREEN + "Все типы оборудования уже существуют в базе данных.")


@database_operation
def fill_in_table_currency_in_postgre_sql(currency_list, connection):
    # Преобразуем список в множество для удаления дубликатов
    currency_set = set(currency_list)

    # Получаем существующие валюты из базы данных
    existing_currencies = set(connection.execute(select(Currency.name)).scalars().all())

    # Находим новые валюты, которых еще нет в базе данных
    new_currencies = currency_set - existing_currencies

    if new_currencies:
        # Подготавливаем данные для вставки
        insert_data = [{"name": currency} for currency in new_currencies]

        # Выполняем вставку новых валют
        stmt = pg_insert(Currency).values(insert_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        result = connection.execute(stmt)
        print(f"Добавлено {result.rowcount} новых названий валют в базу данных PostgreSQL.")
    else:
        print(Fore.GREEN + "Все указанные валюты уже существуют в базе данных.")


def get_set_cities_from_postgre_sql():
    with engine.connect() as connection:
        # Формируем словарь городов из базы данных PostrgeSQL
        cities_dict = {}
        for row in connection.execute(sql_text("SELECT name, id FROM cities")):
            cities_dict[row[0]] = row[1]
    return cities_dict


@database_operation
def copy_table_city_from_sqlite_to_postgresql(cities_list, connection):
    cities_set = set(cities_list)

    # Получаем id страны 'Россия'
    query = select(Country.id).where(Country.name.ilike('Россия'))
    russia_id = connection.execute(query).scalar_one()

    # Получаем существующие города из базы данных
    existing_cities = set(connection.execute(select(City.name)).scalars().all())

    # Находим новые города, которых еще нет в базе данных КИС3
    new_cities = cities_set - existing_cities

    if new_cities:
        # Подготавливаем данные для вставки
        insert_data = [{"name": city, "country_id": russia_id} for city in new_cities]

        # Выполняем вставку новых городов
        stmt = pg_insert(City).values(insert_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        result = connection.execute(stmt)
        print(f"Добавлено {result.rowcount} новых городов в базу данных КИС3.")
    else:
        print(Fore.GREEN + "Все города уже существуют в базе данных.")


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


@database_operation
def fill_in_table_order_status_in_postgre_sql(dummy_list, connection):
    # Получаем существующие статусы
    existing_statuses = connection.execute(select(OrderStatus.name)).fetchall()
    existing_status_set = {row.name for row in existing_statuses}

    insert_data = dummy_list

    # Фильтруем только новые статусы
    new_statuses = [status for status in insert_data if status['name'] not in existing_status_set]

    if new_statuses:
        # Используем insert ... on conflict do nothing для безопасной вставки
        stmt = insert_pg(OrderStatus).values(new_statuses)
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        result = connection.execute(stmt)

        print(Fore.GREEN + f"Добавлено {result.rowcount} новых статусов заказов в базу данных PostgreSQL.")
        logging.info(f"Добавлено {result.rowcount} новых статусов заказов в базу данных PostgreSQL.")
    else:
        print(Fore.YELLOW + "Новых статусов для добавления нет.")
        logging.info("Новых статусов для добавления нет.")

    # Выводим информацию о существующих статусах
    print(Fore.BLUE + f"Всего статусов в базе: {len(existing_status_set)}")
    logging.info(f"Всего статусов в базе: {len(existing_status_set)}")


def get_dict_order_status_from_postgre_sql():
    with engine.connect() as connection:
        # Формируем словарь контрагентов из базы данных PostrgeSQL
        dict_order_status = dict()
        for row in connection.execute(sql_text("SELECT name, id FROM order_statuses")):
            dict_order_status[row[0]] = row[1]
    return dict_order_status


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


def get_dict_people_from_postgre_sql():
    with engine.connect() as connection:
        # Формируем словарь людей из базы данных PostrgeSQL
        dict_people = dict()
        for row in connection.execute(sql_text("SELECT id, surname, name, patronymic  FROM people")):
            dict_people[row[1] + row[2] + row[3]] = row[0]
    return dict_people


@database_operation
def copy_table_box_accounting_in_postgre_sql(list_dict_box_accounting, connection):
    existing_box_accounting = connection.execute(select(BoxAccounting.serial_num)).fetchall()
    existing_box_accounting_set = {row.serial_num for row in existing_box_accounting}

    people_dict_postgre = get_dict_people_from_postgre_sql()
    logging.info(f"Получен словарь людей: {people_dict_postgre}")

    insert_data = []
    update_data = []
    for box_accounting in list_dict_box_accounting:
        key = box_accounting['serial_num']
        box_accounting_data = {
            'serial_num': box_accounting['serial_num'],
            'name': box_accounting['name'],
            'order_id': box_accounting.get('order_id'),
            'scheme_developer_id': people_dict_postgre.get(box_accounting.get('scheme_developer')),
            'assembler_id': people_dict_postgre.get(box_accounting.get('assembler')),
            'programmer_id': people_dict_postgre.get(box_accounting.get('programmer')),
            'tester_id': people_dict_postgre.get(box_accounting.get('tester'))
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


@database_operation
def copy_table_comments_on_orders_from_sqlite_to_postgresql(list_dict_order_comment, connection):
    people_dict_postgre = get_dict_people_from_postgre_sql()
    logging.info(f"Получен словарь людей: {people_dict_postgre}")

    existing_comments = connection.execute(
        select(OrderComment.order_id, OrderComment.moment_of_creation)
    ).fetchall()
    existing_comment_set = {
        (row.order_id, row.moment_of_creation.strftime("%Y-%m-%d %H:%M:%S") if row.moment_of_creation else None)
        for row in existing_comments
    }
    print(existing_comment_set)
    print(list_dict_order_comment)
    insert_data = []
    skipped_count = 0

    for order_comment in list_dict_order_comment:
        order_id = order_comment['order_id']
        moment_of_creation = order_comment['moment_of_creation']

        if (order_id, moment_of_creation) not in existing_comment_set:
            order_comment_data = {
                'order_id': order_id,
                'text': order_comment['text'],
                'moment_of_creation': moment_of_creation,
                'person_id': people_dict_postgre.get(order_comment['person'])
            }
            insert_data.append(order_comment_data)
        else:
            skipped_count += 1

    if insert_data:
        connection.execute(insert(OrderComment), insert_data)
        print(Fore.GREEN + f"Добавлено {len(insert_data)} новых комментариев к заказам")
        logging.info(f"Добавлено {len(insert_data)} новых комментариев к заказам")
    else:
        print(Fore.GREEN + "Новых комментариев для добавления нет.")
        logging.info("Новых комментариев для добавления нет.")

    if skipped_count > 0:
        print(Fore.YELLOW + f"Пропущено {skipped_count} существующих комментариев.")
        logging.info(f"Пропущено {skipped_count} существующих комментариев.")


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
            print("2 - show table 'countries' in PostgreSQL")
            print("3 - show table 'manufacturers' in PostgreSQL")
            print("4 - show table 'equipment_types' in PostgreSQL")
            print("5 - show table 'currencies' in PostgreSQL")
            print("6 - show table 'cities' in PostgreSQL")
            print("7 - show table 'counterparty_form' in PostgreSQL")
            print("8 - show table 'counterparty' in PostgreSQL")
            print("9 - show table 'people' in PostgreSQL")
            print("10 - show table 'works' in PostgreSQL")
            print("11 - show table 'order_statuses' in PostgreSQL")
            print("12 - show table 'orders' in PostgreSQL")
            print("13 - show table 'box_accounting' in PostgreSQL")
            print("14 - show table 'comments_on_orders' in PostgreSQL")

            answer2 = input()

            if answer2 == "0":
                break
            elif answer2 == "1":
                get_all_tables_name_from_postgre_sql()
            elif answer2 == "2":
                # show_table_country_in_postgre_sql()
                show_table_in_postgre_sql("countries")
            elif answer2 == "3":
                # show_table_manufacturers_in_postgre_sql()
                show_table_in_postgre_sql("manufacturers")
            elif answer2 == "4":
                # show_table_equipment_type_in_postgre_sql()
                show_table_in_postgre_sql("equipment_types")
            elif answer2 == "5":
                # show_table_currency_in_postgre_sql()
                show_table_in_postgre_sql("currencies")
            elif answer2 == "6":
                # show_table_city_in_postgre_sql()
                show_table_in_postgre_sql("cities")
            elif answer2 == "7":
                # show_table_counterparty_form_in_postgre_sql()
                show_table_in_postgre_sql("counterparty_form")
            elif answer2 == "8":
                # show_table_counterparties_in_postgre_sql()
                show_table_in_postgre_sql("counterparty")
            elif answer2 == "9":
                # show_table_people_in_postgre_sql()
                show_table_in_postgre_sql("people")
            elif answer2 == "10":
                # show_table_work_in_postgre_sql()
                show_table_in_postgre_sql("works")
            elif answer2 == "11":
                # show_table_order_status_in_postgre_sql()
                show_table_in_postgre_sql("order_statuses")
            elif answer2 == "12":
                # show_table_orders_in_postgre_sql()
                show_table_in_postgre_sql("orders")
            elif answer2 == "13":
                # show_table_box_accounting_in_postgre_sql()
                show_table_in_postgre_sql("box_accounting")
            elif answer2 == "14":
                # show_table_comments_on_orders_in_postgre_sql()
                show_table_in_postgre_sql("comments_on_orders")
            else:
                print(Fore.RED + "Please enter a valid number.")
            print("")

    elif answer1 == "2":
        while answer2 != "e":
            print("")
            print("What copy ?")
            print("1 - copy table 'Country' from sqlite to PostgreSQL")
            print("2 - copy table 'Manufacturers' from sqlite to PostgreSQL")
            print("3 - copy table 'EquipmentType' from sqlite to PostgreSQL")
            print("4 - fill in the table 'Currency'")
            print("5 - copy table 'City' from SQlite to PostgreSQL")
            print("6 - copy table 'CounterpartyForm' from SQlite to PostgreSQL")
            print("7 - copy table 'Counterparties' from SQlite to PostgreSQL")
            print("8 - copy table 'Person' from SQlite to PostgreSQL")
            print("9 - copy table 'Work' from SQlite to PostgreSQL")
            print("10 - fill table 'OrderStatus' from SQlite to PostgreSQL")
            print("11 - copy table 'Order' from SQlite to PostgreSQL")
            print("12 - copy table 'box_accounting' from SQlite to PostgreSQL")
            print("13 - copy table 'comments_on_orders' from SQlite to PostgreSQL")
            print("e - exit")

            answer2 = input()

            if answer2 == "e":
                break
            elif answer2 == "1":
                copy_table_country_from_sqlite_to_postgresql(list(get_all_countries_set_from_sqlite3()))
            elif answer2 == "2":
                copy_table_manufacturers_from_sqlite_to_postgresql(get_all_manufacturers_from_sqlite3())
            elif answer2 == "3":
                copy_table_equipment_type_from_sqlite_to_postgresql(list(get_all_equipment_types_from_sqlite3()))
            elif answer2 == "4":
                fill_in_table_currency_in_postgre_sql(['RUB', 'USD', 'EUR', 'GBP', 'JPY'])
            elif answer2 == "5":
                copy_table_city_from_sqlite_to_postgresql(list(get_set_cities_from_sqlite3()))
            elif answer2 == "6":
                copy_table_companies_form_from_sqlite_to_postgresql(get_set_companies_form_from_sqlite3())
            elif answer2 == "7":
                copy_table_counterparties_from_sqlite_to_postgresql(get_list_dict_companies_from_sqlite3())
            elif answer2 == "8":
                copy_table_people_from_sqlite_to_postgresql(get_list_dict_person_from_sqlite3())
            elif answer2 == "9":
                copy_table_work_from_sqlite_to_postgresql(get_list_dict_work_from_sqlite3())
            elif answer2 == "10":
                fill_in_table_order_status_in_postgre_sql(
                    [
                        {"name": 'Не определён'},
                        {"name": 'На согласовании'},
                        {"name": 'В работе'},
                        {"name": 'Просрочено'},
                        {"name": 'Выполнено в срок'},
                        {"name": 'Выполнено НЕ в срок'},
                        {"name": 'Не согласовано'},
                        {"name": 'На паузе'}
                    ])  # Передаем список
            elif answer2 == "11":
                copy_table_orders_from_sqlite_to_postgresql(get_list_dict_orders_from_sqlite3())
            elif answer2 == "12":
                copy_table_box_accounting_in_postgre_sql(get_list_dict_box_accounting_from_sqlite3())
            elif answer2 == "13":
                copy_table_comments_on_orders_from_sqlite_to_postgresql(get_list_dict_order_comment_from_sqlite3())
            else:
                print(Fore.RED + "Please enter a valid number.")
            print("")

    else:
        print(Fore.RED + "Please enter a valid number.")
