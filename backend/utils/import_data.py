# utils/import_data.py
"""
Модуль импорта данных из КИС2(БД SQlite3) в КИС3(БД PostgreSQL).
Получение данных из КИС2(БД SQlite3) реализовано через Django Rest API.
"""
import sys
import os
from datetime import datetime, timedelta

from colorama import init, Fore
from typing import Dict, Set, Any

# Добавляем родительскую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kis2.DjangoRestAPI import create_countries_set_from_kis2, create_tasks_list_dict_from_kis2, \
    create_order_comments_list_dict_from_kis2, create_boxes_list_dict_from_kis2, \
    create_timings_list_dict_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_box_accounting_list_dict_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_companies_list_dict_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_list_dict_manufacturers  # noqa: E402
from kis2.DjangoRestAPI import create_equipment_type_set_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_money_set_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_cities_set_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_companies_form_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_person_list_dict_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_works_list_dict_from_kis2  # noqa: E402
from kis2.DjangoRestAPI import create_orders_list_dict_from_kis2  # noqa: E402

from database import SyncSession, test_sync_connection  # noqa: E402
from models.models import Country, TaskStatus, TaskPaymentStatus, Task, OrderComment, ControlCabinet, \
    ControlCabinetMaterial, Ip, Timing  # noqa: E402
from models.models import BoxAccounting  # noqa: E402
from models.models import Manufacturer  # noqa: E402
from models.models import Counterparty  # noqa: E402
from models.models import CounterpartyForm  # noqa: E402
from models.models import City  # noqa: E402
from models.models import OrderStatus  # noqa: E402
from models.models import EquipmentType  # noqa: E402
from models.models import Currency  # noqa: E402
from models.models import Person  # noqa: E402
from models.models import Work  # noqa: E402
from models.models import Order  # noqa: E402

# Инициализируем colorama
init(autoreset=True)


def commit_and_summarize_import(session, result, entity_type='записей'):
    """
    Сохраняет изменения в базе данных и формирует сводку по результатам импорта.
    """
    if result['added'] > 0 or result['updated'] > 0:
        session.commit()
        summary = []
        if result['added'] > 0:
            summary.append(f"добавлено {result['added']} новых {entity_type}")
        if result['updated'] > 0:
            summary.append(f"обновлено {result['updated']} существующих {entity_type}")
        if result['unchanged'] > 0:
            summary.append(f"без изменений {result['unchanged']} {entity_type}")
        print(Fore.GREEN + f"Результат импорта {entity_type}: {', '.join(summary)}")
    else:
        print(Fore.YELLOW + f"Все {entity_type} ({result['unchanged']}) уже существуют и актуальны.")
    result['status'] = 'success'
    return result


def get_existing_items(session, model) -> Set[str]:
    """
    Получает множество существующих элементов из базы данных по модели.

    Args:
        session: Текущая сессия базы данных
        model: Класс модели SQLAlchemy

    Returns:
        Set[str]: Множество имен существующих элементов
    """
    query = session.query(model.name).all()
    return set(item[0] for item in query)


def bulk_insert_new_items(session, model, new_items: Set[str], result: Dict[str, Any]) -> None:
    """
    Выполняет массовую вставку новых элементов в базу данных.

    Args:
        session: Текущая сессия базы данных
        model: Класс модели SQLAlchemy
        new_items: Множество новых элементов для вставки
        result: Словарь результатов для обновления поля 'added'
    """
    if new_items:
        insert_data = [{"name": item} for item in new_items]
        session.bulk_insert_mappings(model.__mapper__, insert_data)
        result['added'] = len(new_items)


def import_countries_from_kis2() -> Dict[str, any]:
    """
    Импортировать страны из КИС2 в базу данных.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_countries_set = create_countries_set_from_kis2(debug=False)
        if not kis2_countries_set:
            print(Fore.YELLOW + "Не удалось получить страны из КИС2 или список пуст.")
            return result

        with SyncSession() as session:
            try:
                existing_countries = get_existing_items(session, Country)
                new_countries = kis2_countries_set - existing_countries
                result['unchanged'] = len(kis2_countries_set & existing_countries)

                bulk_insert_new_items(session, Country, new_countries, result)
                return commit_and_summarize_import(session, result, "стран")
            except Exception as db_error:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте стран: {db_error}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта стран: {e}")
        return result


def import_manufacturers_from_kis2() -> Dict[str, any]:
    """
    Импортировать производителей из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_manufacturers_list = create_list_dict_manufacturers(debug=False)
        if not kis2_manufacturers_list:
            print(Fore.YELLOW + "Не удалось получить производителей из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_manufacturers_list)} производителей из КИС2.")
        with SyncSession() as session:
            try:
                manufacturers_query = session.query(Manufacturer.name).all()
                existing_manufacturers = set(m[0] for m in manufacturers_query)
                countries_query = session.query(Country.id, Country.name).all()
                countries_dict = {name: id for id, name in countries_query}

                unique_countries = set(item['country'] for item in kis2_manufacturers_list)
                missing_countries = unique_countries - set(countries_dict.keys())
                if missing_countries:
                    print(Fore.YELLOW + f"Обнаружено {len(missing_countries)} отсутствующих стран. Добавление...")
                    for country_name in missing_countries:
                        session.add(Country(name=country_name))
                    session.commit()
                    countries_query = session.query(Country.id, Country.name).all()
                    countries_dict = {name: id for id, name in countries_query}

                for manufacturer_data in kis2_manufacturers_list:
                    name = manufacturer_data['name']
                    country_name = manufacturer_data['country']
                    if name in existing_manufacturers:
                        result['unchanged'] += 1
                        continue

                    country_id = countries_dict.get(country_name)
                    if not country_id:
                        print(Fore.RED + f"Не удалось найти ID для страны '{country_name}'. Пропуск '{name}'.")
                        continue

                    session.add(Manufacturer(name=name, country_id=country_id))
                    result['added'] += 1
                return commit_and_summarize_import(session, result, "производителей")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте производителей: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта производителей: {e}")
        return result


def import_equipment_type_from_kis2() -> Dict[str, any]:
    """
    Импортировать типы оборудования из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_equipment_types_set = create_equipment_type_set_from_kis2(debug=False)
        if not kis2_equipment_types_set:
            print(Fore.YELLOW + "Не удалось получить типы оборудования из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_equipment_types_set)} типов оборудования из КИС2.")
        with SyncSession() as session:
            try:
                existing_types = get_existing_items(session, EquipmentType)
                new_types = kis2_equipment_types_set - existing_types
                result['unchanged'] = len(kis2_equipment_types_set & existing_types)

                bulk_insert_new_items(session, EquipmentType, new_types, result)
                return commit_and_summarize_import(session, result, "типов оборудования")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте типов оборудования: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта типов оборудования: {e}")
        return result


def import_currency_from_kis2() -> Dict[str, any]:
    """
    Импортировать типы валют из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_currencies_set = create_money_set_from_kis2(debug=False)
        if not kis2_currencies_set:
            print(Fore.YELLOW + "Не удалось получить валюты из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_currencies_set)} валют из КИС2.")
        with SyncSession() as session:
            try:
                existing_currencies = get_existing_items(session, Currency)
                new_currencies = kis2_currencies_set - existing_currencies
                result['unchanged'] = len(kis2_currencies_set & existing_currencies)

                bulk_insert_new_items(session, Currency, new_currencies, result)
                return commit_and_summarize_import(session, result, "валют")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте валют: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта валют: {e}")
        return result


def import_cities_from_kis2() -> Dict[str, any]:
    """
    Импортирует названия городов из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_cities_set = create_cities_set_from_kis2(debug=False)
        if not kis2_cities_set:
            print(Fore.YELLOW + "Не удалось получить города из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_cities_set)} городов из КИС2.")
        with SyncSession() as session:
            try:
                cities_query = session.query(City.name).all()
                existing_cities = set(c[0] for c in cities_query)
                russia = session.query(Country).filter(Country.name == "Россия").first()
                if not russia:
                    print(Fore.YELLOW + "Страна 'Россия' не найдена. Создание...")
                    russia = Country(name="Россия")
                    session.add(russia)
                    session.commit()

                new_cities = kis2_cities_set - existing_cities
                result['unchanged'] = len(kis2_cities_set & existing_cities)

                if new_cities:
                    insert_data = [{"name": c, "country_id": russia.id} for c in new_cities]
                    session.bulk_insert_mappings(City.__mapper__, insert_data)
                    result['added'] = len(new_cities)
                return commit_and_summarize_import(session, result, "городов")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте городов: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта городов: {e}")
        return result


def import_counterparty_from_kis2() -> Dict[str, any]:
    """
    Импортирует названия форм контрагентов из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_forms_set = create_companies_form_from_kis2(debug=False)
        if not kis2_forms_set:
            print(Fore.YELLOW + "Не удалось получить формы контрагентов из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_forms_set)} форм контрагентов из КИС2.")
        with SyncSession() as session:
            try:
                forms_query = session.query(CounterpartyForm.name).all()
                existing_forms = set(f[0] for f in forms_query)
                new_forms = kis2_forms_set - existing_forms
                result['unchanged'] = len(kis2_forms_set & existing_forms)

                if new_forms:
                    insert_data = [{"name": f} for f in new_forms]
                    session.bulk_insert_mappings(CounterpartyForm.__mapper__, insert_data)
                    result['added'] = len(new_forms)
                return commit_and_summarize_import(session, result, "форм контрагентов")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте форм контрагентов: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта форм контрагентов: {e}")
        return result


def import_companies_from_kis2() -> Dict[str, any]:
    """
    Импортирует контрагентов (компании) из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_companies_list = create_companies_list_dict_from_kis2(debug=False)
        if not kis2_companies_list:
            print(Fore.YELLOW + "Не удалось получить компании из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_companies_list)} компаний из КИС2.")
        with SyncSession() as session:
            try:
                existing_companies = {c[1]: {'id': c[0], 'form_id': c[2], 'city_id': c[3], 'note': c[4]}
                                      for c in session.query(Counterparty.id, Counterparty.name,
                                                             Counterparty.form_id, Counterparty.city_id,
                                                             Counterparty.note).all()}
                forms_dict = {name: id for id, name in session.query(CounterpartyForm.id, CounterpartyForm.name).all()}
                form_id_to_name = {id: name for name, id in forms_dict.items()}
                cities_dict = {name: id for id, name in session.query(City.id, City.name).all()}
                city_id_to_name = {id: name for name, id in cities_dict.items()}

                for company_data in kis2_companies_list:
                    name = company_data['name']
                    form_id = forms_dict.get(company_data['form'])
                    if not form_id:
                        print(Fore.RED + f"Не найден ID для формы '{company_data['form']}'. Пропуск '{name}'.")
                        continue
                    city_id = cities_dict.get(company_data['city']) if company_data['city'] else None
                    note = company_data['note']

                    if name in existing_companies:
                        existing = existing_companies[name]
                        needs_update = False
                        update_details = []
                        if existing['form_id'] != form_id:
                            needs_update = True
                            update_details.append(
                                f"форма с '{form_id_to_name.get(existing['form_id'])}' на '{company_data['form']}'")
                        if existing['city_id'] != city_id:
                            needs_update = True
                            old_city = city_id_to_name.get(existing['city_id'], "отсутствует")
                            new_city = company_data['city'] or "отсутствует"
                            update_details.append(f"город с '{old_city}' на '{new_city}'")
                        if existing['note'] != note:
                            needs_update = True
                            update_details.append("примечание")

                        if needs_update:
                            counterparty = session.get(Counterparty, existing['id'])
                            counterparty.form_id = form_id
                            counterparty.city_id = city_id
                            counterparty.note = note
                            result['updated'] += 1
                            print(Fore.BLUE + f"Обновлена компания '{name}': {', '.join(update_details)}")
                        else:
                            result['unchanged'] += 1
                    else:
                        session.add(Counterparty(name=name, form_id=form_id, city_id=city_id, note=note))
                        result['added'] += 1
                return commit_and_summarize_import(session, result, "компаний")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте компаний: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта компаний: {e}")
        return result


def import_person_from_kis2() -> Dict[str, any]:
    """
    Импортирует людей (персоны) из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_persons_list = create_person_list_dict_from_kis2(debug=False)
        if not kis2_persons_list:
            print(Fore.YELLOW + "Не удалось получить людей из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_persons_list)} людей из КИС2.")
        with SyncSession() as session:
            try:
                existing_persons = {
                    f"{p[3]}|{p[1]}|{p[2] or ''}": {'id': p[0], 'phone': p[4], 'email': p[5], 'counterparty_id': p[6]}
                    for p in session.query(Person.id, Person.name, Person.patronymic,
                                           Person.surname, Person.phone, Person.email,
                                           Person.counterparty_id).all()}
                companies_dict = {name: id for id, name in session.query(Counterparty.id, Counterparty.name).all()}

                for person_data in kis2_persons_list:
                    name = person_data['name']
                    patronymic = person_data['patronymic']
                    surname = person_data['surname']
                    phone = person_data['phone']
                    email = person_data['email']
                    company_id = companies_dict.get(person_data['company']) if person_data['company'] else None
                    person_key = f"{surname}|{name}|{patronymic or ''}"

                    if person_key in existing_persons:
                        existing = existing_persons[person_key]
                        needs_update = False
                        update_details = []
                        if existing['phone'] != phone:
                            needs_update = True
                            update_details.append(
                                f"телефон с '{existing['phone'] or 'отсутствует'}' на '{phone or 'отсутствует'}'")
                        if existing['email'] != email:
                            needs_update = True
                            update_details.append(
                                f"email с '{existing['email'] or 'отсутствует'}' на '{email or 'отсутствует'}'")
                        if existing['counterparty_id'] != company_id:
                            needs_update = True
                            old_company = next(
                                (n for n, i in companies_dict.items() if i == existing['counterparty_id']),
                                "отсутствует")
                            new_company = person_data['company'] or "отсутствует"
                            update_details.append(f"компания с '{old_company}' на '{new_company}'")

                        if needs_update:
                            person = session.get(Person, existing['id'])
                            person.phone = phone
                            person.email = email
                            person.counterparty_id = company_id
                            result['updated'] += 1
                            print(Fore.BLUE + f"Обновлен человек '{surname} {name}': {', '.join(update_details)}")
                        else:
                            result['unchanged'] += 1
                    else:
                        session.add(Person(name=name, patronymic=patronymic, surname=surname,
                                           phone=phone, email=email, counterparty_id=company_id, active=True))
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлен новый человек: {surname} {name}")
                return commit_and_summarize_import(session, result, "людей")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте людей: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта людей: {e}")
        return result


def import_works_from_kis2() -> Dict[str, any]:
    """
    Импортирует работы из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_works_list = create_works_list_dict_from_kis2(debug=False)
        if not kis2_works_list:
            print(Fore.YELLOW + "Не удалось получить работы из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_works_list)} работ из КИС2.")
        with SyncSession() as session:
            try:
                existing_works = {w[1]: {'id': w[0], 'description': w[2]}
                                  for w in session.query(Work.id, Work.name, Work.description).all()}

                for work_data in kis2_works_list:
                    name = work_data['name']
                    description = work_data.get('description', "")
                    if name in existing_works:
                        existing = existing_works[name]
                        if existing['description'] != description:
                            work = session.get(Work, existing['id'])
                            work.description = description
                            result['updated'] += 1
                            print(Fore.BLUE + f"Обновлена работа '{name}': изменено описание")
                        else:
                            result['unchanged'] += 1
                    else:
                        session.add(Work(name=name, description=description, active=True))
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлена новая работа: {name}")
                return commit_and_summarize_import(session, result, "работ")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте работ: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта работ: {e}")
        return result


def ensure_order_statuses_exist() -> Dict[str, any]:
    """
    Проверяет наличие стандартных статусов заказов в базе данных, создает отсутствующие и обновляет описания.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        standard_statuses = [
            {"id": 1, "name": "Не определён", "description": "Статус заказа не определен"},
            {"id": 2, "name": "На согласовании", "description": "Заказ находится на этапе согласования"},
            {"id": 3, "name": "В работе", "description": "Заказ находится в процессе выполнения"},
            {"id": 4, "name": "Просрочено", "description": "Срок выполнения заказа просрочен"},
            {"id": 5, "name": "Выполнено в срок", "description": "Заказ выполнен в установленный срок"},
            {"id": 6, "name": "Выполнено НЕ в срок", "description": "Заказ выполнен с нарушением установленного срока"},
            {"id": 7, "name": "Не согласовано", "description": "Заказ не согласован"},
            {"id": 8, "name": "На паузе", "description": "Выполнение заказа приостановлено"}
        ]
        with SyncSession() as session:
            try:
                existing_statuses = {s.id: s for s in session.query(OrderStatus).all()}
                new_statuses = []
                updates = []

                for status in standard_statuses:
                    if status["id"] not in existing_statuses:
                        new_statuses.append(status)
                        result['added'] += 1
                    elif existing_statuses[status["id"]].description != status["description"]:
                        updates.append(status)
                        result['updated'] += 1
                    else:
                        result['unchanged'] += 1

                if new_statuses:
                    session.bulk_insert_mappings(OrderStatus.__mapper__, new_statuses)
                if updates:
                    session.bulk_update_mappings(OrderStatus.__mapper__, updates)
                return commit_and_summarize_import(session, result, "статусов заказов")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при работе со статусами заказов: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении проверки статусов заказов: {e}")
        return result


def import_orders_from_kis2() -> Dict[str, any]:
    """
    Импортирует заказы из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_orders_list = create_orders_list_dict_from_kis2(debug=False)
        if not kis2_orders_list:
            print(Fore.YELLOW + "Не удалось получить заказы из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_orders_list)} заказов из КИС2.")
        with SyncSession() as session:
            try:
                # Получаем существующие заказы
                existing_orders = {o.serial: o for o in session.query(Order).all()}
                # Получаем словари для связей
                customers_dict = {name: id for id, name in session.query(Counterparty.id, Counterparty.name).all()}
                works_dict = {name: id for id, name in session.query(Work.id, Work.name).all()}
                status_dict = {name: id for id, name in session.query(OrderStatus.id, OrderStatus.name).all()}

                # Проверяем наличие всех статусов заказов
                ensure_order_statuses_exist()

                for order_data in kis2_orders_list:
                    serial = order_data['serial']
                    name = order_data['name']
                    customer_name = order_data['customer']
                    priority = order_data['priority'] if order_data['priority'] > 0 and order_data[
                        'priority'] < 11 else None
                    # Получаем id статуса из словаря по текстовому статусу
                    status_text = order_data['status']
                    status_id = status_dict.get(status_text, 1)  # По умолчанию 1 (Не определён)

                    # Конвертация строк дат и времени в объекты datetime
                    start_moment = datetime.strptime(order_data['start_moment'], "%Y-%m-%dT%H:%M:%SZ") if order_data[
                        'start_moment'] else None
                    deadline_moment = datetime.strptime(order_data['dedline_moment'], "%Y-%m-%dT%H:%M:%SZ") if \
                        order_data['dedline_moment'] else None
                    end_moment = datetime.strptime(order_data['end_moment'], "%Y-%m-%dT%H:%M:%SZ") if order_data[
                        'end_moment'] else None

                    # Получаем customer_id
                    if customer_name and customer_name in customers_dict:
                        customer_id = customers_dict[customer_name]
                    else:
                        print(Fore.YELLOW + f"Не найден заказчик '{customer_name}' для заказа {serial}. Пропуск.")
                        continue

                    # Финансовые данные
                    materials_cost = order_data.get('materialsCost', 0)
                    materials_paid = order_data.get('materialsPaid', False)
                    products_cost = order_data.get('productsCost', 0)
                    products_paid = order_data.get('productsPaid', False)
                    work_cost = order_data.get('workCost', 0)
                    work_paid = order_data.get('workPaid', False)
                    debt = order_data.get('debt', 0)
                    debt_paid = order_data.get('debtPaid', False)

                    # Получаем список работ
                    order_works = order_data.get('works', [])

                    # Если заказ уже существует, обновляем его
                    if serial in existing_orders:
                        order = existing_orders[serial]
                        needs_update = False
                        update_details = []

                        # Проверяем изменения в основных полях
                        if order.name != name:
                            order.name = name
                            needs_update = True
                            update_details.append("название")

                        if order.customer_id != customer_id:
                            order.customer_id = customer_id
                            needs_update = True
                            update_details.append("заказчик")

                        if order.priority != priority:
                            order.priority = priority
                            needs_update = True
                            update_details.append("приоритет")

                        if order.status_id != status_id:
                            order.status_id = status_id
                            needs_update = True
                            update_details.append("статус")

                        if order.start_moment != start_moment:
                            order.start_moment = start_moment
                            needs_update = True
                            update_details.append("дата начала")

                        if order.deadline_moment != deadline_moment:
                            order.deadline_moment = deadline_moment
                            needs_update = True
                            update_details.append("дедлайн")

                        if order.end_moment != end_moment:
                            order.end_moment = end_moment
                            needs_update = True
                            update_details.append("дата окончания")

                        # Проверяем изменения в финансовых данных
                        if order.materials_cost != materials_cost:
                            order.materials_cost = materials_cost
                            needs_update = True
                            update_details.append("стоимость материалов")

                        if order.materials_paid != materials_paid:
                            order.materials_paid = materials_paid
                            needs_update = True
                            update_details.append("оплата материалов")

                        if order.products_cost != products_cost:
                            order.products_cost = products_cost
                            needs_update = True
                            update_details.append("стоимость товаров")

                        if order.products_paid != products_paid:
                            order.products_paid = products_paid
                            needs_update = True
                            update_details.append("оплата товаров")

                        if order.work_cost != work_cost:
                            order.work_cost = work_cost
                            needs_update = True
                            update_details.append("стоимость работ")

                        if order.work_paid != work_paid:
                            order.work_paid = work_paid
                            needs_update = True
                            update_details.append("оплата работ")

                        if order.debt != debt:
                            order.debt = debt
                            needs_update = True
                            update_details.append("задолженность")

                        if order.debt_paid != debt_paid:
                            order.debt_paid = debt_paid
                            needs_update = True
                            update_details.append("оплата задолженности")

                        # Обновляем связи с работами
                        existing_works = {work.name for work in order.works}
                        new_works = set(order_works) - existing_works
                        removed_works = existing_works - set(order_works)

                        if new_works or removed_works:
                            needs_update = True
                            # Удаляем работы, которых больше нет в заказе
                            if removed_works:
                                for work_name in removed_works:
                                    work_to_remove = next((w for w in order.works if w.name == work_name), None)
                                    if work_to_remove:
                                        order.works.remove(work_to_remove)
                                        update_details.append(f"удалена работа '{work_name}'")

                            # Добавляем новые работы
                            if new_works:
                                for work_name in new_works:
                                    work_id = works_dict.get(work_name)
                                    if work_id:
                                        work = session.query(Work).get(work_id)
                                        if work:
                                            order.works.append(work)
                                            update_details.append(f"добавлена работа '{work_name}'")

                        if needs_update:
                            result['updated'] += 1
                            print(Fore.BLUE + f"Обновлен заказ '{serial}': {', '.join(update_details)}")
                        else:
                            result['unchanged'] += 1
                    else:
                        # Создаем новый заказ
                        new_order = Order(
                            serial=serial,
                            name=name,
                            customer_id=customer_id,
                            priority=priority,
                            status_id=status_id,
                            start_moment=start_moment,
                            deadline_moment=deadline_moment,
                            end_moment=end_moment,
                            materials_cost=materials_cost,
                            materials_paid=materials_paid,
                            products_cost=products_cost,
                            products_paid=products_paid,
                            work_cost=work_cost,
                            work_paid=work_paid,
                            debt=debt,
                            debt_paid=debt_paid
                        )

                        # Добавляем связи с работами
                        for work_name in order_works:
                            work_id = works_dict.get(work_name)
                            if work_id:
                                work = session.query(Work).get(work_id)
                                if work:
                                    new_order.works.append(work)

                        session.add(new_order)
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлен новый заказ: {serial} - {name}")

                return commit_and_summarize_import(session, result, "заказов")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте заказов: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта заказов: {e}")
        return result


def import_box_accounting_from_kis2() -> Dict[str, any]:
    """
    Импортирует данные об изготовленных шкафах из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_boxes_list = create_box_accounting_list_dict_from_kis2(debug=False)
        if not kis2_boxes_list:
            print(Fore.YELLOW + "Не удалось получить данные о шкафах из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_boxes_list)} шкафов из КИС2.")
        with SyncSession() as session:
            try:
                # Получаем существующие шкафы
                existing_boxes = {b.serial_num: b for b in session.query(BoxAccounting).all()}

                # Создаем множество существующих заказов из КИС3
                orders_set = set(serial[0] for serial in session.query(Order.serial).all())

                # Создаем вспомогательный словарь для поиска людей
                persons_by_name = {}
                for person in session.query(Person).all():
                    full_name = f"{person.surname} {person.name}"
                    if person.patronymic:
                        full_name += f" {person.patronymic}"
                    persons_by_name[full_name] = person.id

                # Проходим по списку шкафов из КИС2
                for box_data in kis2_boxes_list:
                    serial_num = box_data['serial_num']
                    name = box_data['name']
                    order_serial = box_data['order_serial']
                    scheme_developer_name = box_data['scheme_developer']
                    assembler_name = box_data['assembler']
                    programmer_name = box_data['programmer']
                    tester_name = box_data['tester']

                    # Проверяем, существует ли заказ
                    if order_serial not in orders_set:
                        print(Fore.YELLOW + f"Не найден заказ '{order_serial}' для шкафа {serial_num}. Пропуск.")
                        continue

                    # Ищем ID разработчика схемы
                    scheme_developer_id = persons_by_name.get(scheme_developer_name)
                    if not scheme_developer_id and scheme_developer_name:
                        print(Fore.YELLOW + f"Не найден разработчик схемы '{scheme_developer_name}'"
                                            f" для шкафа {serial_num}. Пропуск.")
                        continue

                    # Ищем ID сборщика
                    assembler_id = persons_by_name.get(assembler_name)
                    if not assembler_id and assembler_name:
                        print(Fore.YELLOW + f"Не найден сборщик '{assembler_name}' для шкафа {serial_num}. Пропуск.")
                        continue

                    # Ищем ID программиста
                    programmer_id = None
                    if programmer_name:
                        programmer_id = persons_by_name.get(programmer_name)
                        if not programmer_id:
                            print(Fore.YELLOW + f"Не найден программист '{programmer_name}' для шкафа {serial_num}."
                                                f"Программист будет пропущен.")

                    # Ищем ID тестировщика
                    tester_id = persons_by_name.get(tester_name)
                    if not tester_id and tester_name:
                        print(Fore.YELLOW + f"Не найден тестировщик '{tester_name}' для шкафа {serial_num}. Пропуск.")
                        continue

                    # Если шкаф уже существует, проверяем необходимость обновления
                    if serial_num in existing_boxes:
                        box = existing_boxes[serial_num]
                        needs_update = False
                        update_details = []

                        # Проверяем изменения в полях
                        if box.name != name:
                            box.name = name
                            needs_update = True
                            update_details.append("название")

                        if box.order_id != order_serial:
                            box.order_id = order_serial
                            needs_update = True
                            update_details.append("заказ")

                        if box.scheme_developer_id != scheme_developer_id:
                            box.scheme_developer_id = scheme_developer_id
                            needs_update = True
                            update_details.append("разработчик схемы")

                        if box.assembler_id != assembler_id:
                            box.assembler_id = assembler_id
                            needs_update = True
                            update_details.append("сборщик")

                        if box.programmer_id != programmer_id:
                            box.programmer_id = programmer_id
                            needs_update = True
                            update_details.append("программист")

                        if box.tester_id != tester_id:
                            box.tester_id = tester_id
                            needs_update = True
                            update_details.append("тестировщик")

                        if needs_update:
                            result['updated'] += 1
                            print(Fore.BLUE + f"Обновлен шкаф '{serial_num}': {', '.join(update_details)}")
                        else:
                            result['unchanged'] += 1
                    else:
                        # Создаем новый шкаф
                        new_box = BoxAccounting(
                            serial_num=serial_num,
                            name=name,
                            order_id=order_serial,
                            scheme_developer_id=scheme_developer_id,
                            assembler_id=assembler_id,
                            programmer_id=programmer_id,
                            tester_id=tester_id
                        )
                        session.add(new_box)
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлен новый шкаф: {serial_num} - {name}")

                return commit_and_summarize_import(session, result, "записи о серийных номерах шкафов")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте шкафов: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта шкафов: {e}")
        return result


def parse_iso_duration(duration_str: str) -> timedelta | None:
    """
    Преобразует строку длительности в формате ISO 8601 (например, 'P0DT01H00M00S') в timedelta.
    """
    if not duration_str or not duration_str.startswith('P'):
        return None

    days = 0
    hours = 0
    minutes = 0
    seconds = 0

    # Убираем 'P' и разделяем на части до и после 'T'
    duration_str = duration_str[1:]  # Убираем 'P'
    if 'T' in duration_str:
        days_part, time_part = duration_str.split('T')
    else:
        days_part = duration_str
        time_part = ''

    # Парсим дни
    if 'D' in days_part:
        days = int(days_part.split('D')[0])

    # Парсим время
    if 'H' in time_part:
        hours_part = time_part.split('H')[0]
        hours = int(hours_part[-2:]) if hours_part else 0
        time_part = time_part.split('H')[1]

    if 'M' in time_part:
        minutes_part = time_part.split('M')[0]
        minutes = int(minutes_part[-2:]) if minutes_part else 0
        time_part = time_part.split('M')[1]

    if 'S' in time_part:
        seconds = int(time_part.split('S')[0])

    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def import_tasks_from_kis2() -> Dict[str, any]:
    """
    Импортирует задачи из КИС2 в базу данных КИС3, используя id из КИС2 как первичный ключ.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_tasks_list = create_tasks_list_dict_from_kis2(debug=False)
        if not kis2_tasks_list:
            print(Fore.YELLOW + "Не удалось получить задачи из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_tasks_list)} задач из КИС2.")
        with SyncSession() as session:
            try:
                # Проверим и создадим стандартные статусы задач
                ensure_task_statuses_exist(session)

                # Проверим и создадим стандартные статусы оплаты
                ensure_payment_statuses_exist(session)

                # Получаем существующие задачи по id
                existing_tasks = {t.id: t for t in session.query(Task).all()}

                # Создаем словари для связей
                task_statuses_dict = {}
                for id, name in session.query(TaskStatus.id, TaskStatus.name).all():
                    task_statuses_dict[name] = id

                payment_statuses_dict = {}
                for id, name in session.query(TaskPaymentStatus.id, TaskPaymentStatus.name).all():
                    payment_statuses_dict[name] = id

                # Получаем словарь персон для связи с исполнителями задач
                persons_by_name = {}
                for person in session.query(Person).all():
                    full_name = f"{person.surname} {person.name}"
                    if person.patronymic:
                        full_name += f" {person.patronymic}"
                    persons_by_name[full_name] = person.id

                # Обрабатываем каждую задачу из КИС2
                for task_data in kis2_tasks_list:
                    kis2_id = task_data.get('id')
                    if kis2_id is None:
                        print(Fore.YELLOW + f"Пропущена задача '{task_data['name']}' без ID из КИС2.")
                        continue  # Пропускаем задачи без ID

                    name = task_data['name']
                    description = task_data.get('description') or ""

                    # Получаем ID исполнителя
                    executor_id = None
                    if task_data['executor']:
                        executor_id = persons_by_name.get(task_data['executor'])
                        if not executor_id:
                            print(Fore.YELLOW + f"Не найден исполнитель '{task_data['executor']}' для задачи '{name}'.")

                    # Получаем ID статуса задачи
                    status_id = task_statuses_dict.get(task_data['status'], 1)  # "Не начата" по умолчанию

                    # Получаем ID статуса оплаты, "Нет оплаты" по умолчанию
                    payment_status_id = payment_statuses_dict.get(task_data['payment_status'], 1)

                    # Преобразование строк дат в объекты datetime
                    if 'creation_moment' in task_data:
                        creation_moment = datetime.strptime(task_data['creation_moment'], "%Y-%m-%dT%H:%M:%SZ")
                    else:
                        creation_moment = None

                    if 'start_moment' in task_data:
                        start_moment = datetime.strptime(task_data['start_moment'], "%Y-%m-%dT%H:%M:%SZ")
                    else:
                        start_moment = None

                    if 'end_moment' in task_data:
                        end_moment = datetime.strptime(task_data['end_moment'], "%Y-%m-%dT%H:%M:%SZ")
                    else:
                        end_moment = None

                    # Преобразование длительностей из строки в timedelta
                    planned_duration = parse_iso_duration(task_data.get('planned_duration'))
                    actual_duration = parse_iso_duration(task_data.get('actual_duration'))

                    # Получаем ссылки на родительскую и корневую задачи
                    parent_task_id = task_data.get('parent_task_id')
                    root_task_id = task_data.get('root_task_id')

                    # Проверяем существование задачи в КИС3 по ID из КИС2
                    if kis2_id in existing_tasks:
                        # Обновляем существующую задачу
                        task = existing_tasks[kis2_id]
                        needs_update = False
                        update_details = []

                        if task.name != name:
                            task.name = name
                            needs_update = True
                            update_details.append("название")
                        if task.description != description:
                            task.description = description
                            needs_update = True
                            update_details.append("описание")
                        if task.executor_id != executor_id:
                            task.executor_id = executor_id
                            needs_update = True
                            update_details.append("исполнитель")
                        if task.status_id != status_id:
                            task.status_id = status_id
                            needs_update = True
                            update_details.append("статус")
                        if task.payment_status_id != payment_status_id:
                            task.payment_status_id = payment_status_id
                            needs_update = True
                            update_details.append("статус оплаты")
                        if task.planned_duration != planned_duration:
                            task.planned_duration = planned_duration
                            needs_update = True
                            update_details.append("планируемая длительность")
                        if task.actual_duration != actual_duration:
                            task.actual_duration = actual_duration
                            needs_update = True
                            update_details.append("фактическая длительность")
                        if task.creation_moment != creation_moment:
                            task.creation_moment = creation_moment
                            needs_update = True
                            update_details.append("дата создания")
                        if task.start_moment != start_moment:
                            task.start_moment = start_moment
                            needs_update = True
                            update_details.append("дата начала")
                        if task.end_moment != end_moment:
                            task.end_moment = end_moment
                            needs_update = True
                            update_details.append("дата завершения")
                        if task.price != task_data.get('cost'):
                            task.price = task_data.get('cost')
                            needs_update = True
                            update_details.append("стоимость")
                        if task.order_serial != task_data.get('order_id'):
                            task.order_serial = task_data.get('order_id')
                            needs_update = True
                            update_details.append("заказ")
                        if task.parent_task_id != parent_task_id:
                            task.parent_task_id = parent_task_id
                            needs_update = True
                            update_details.append("родительская задача")
                        if task.root_task_id != root_task_id:
                            task.root_task_id = root_task_id
                            needs_update = True
                            update_details.append("корневая задача")

                        if needs_update:
                            result['updated'] += 1
                            print(Fore.BLUE + f"Обновлена задача ID={kis2_id} ('{name}'): {', '.join(update_details)}")
                        else:
                            result['unchanged'] += 1
                    else:
                        # Создаем новую задачу с ID из КИС2
                        new_task = Task(
                            id=kis2_id,  # Используем ID из КИС2
                            name=name,
                            description=description,
                            executor_id=executor_id,
                            status_id=status_id,
                            payment_status_id=payment_status_id,
                            planned_duration=planned_duration,
                            actual_duration=actual_duration,
                            creation_moment=creation_moment,
                            start_moment=start_moment,
                            end_moment=end_moment,
                            price=task_data.get('cost'),
                            order_serial=task_data.get('order_id'),
                            parent_task_id=parent_task_id,
                            root_task_id=root_task_id
                        )
                        session.add(new_task)
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлена новая задача ID={kis2_id} ('{name}')")

                return commit_and_summarize_import(session, result, "задач")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте задач: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта задач: {e}")
        return result


def ensure_task_statuses_exist(session) -> None:
    """
    Проверяет наличие стандартных статусов задач в базе данных, создает отсутствующие и обновляет описания.
    """
    standard_statuses = [
        {"id": 1, "name": "Не начата", "description": "Задача еще не начата"},
        {"id": 2, "name": "В работе", "description": "Задача находится в процессе выполнения"},
        {"id": 3, "name": "На паузе", "description": "Выполнение задачи приостановлено"},
        {"id": 4, "name": "Завершена", "description": "Задача успешно завершена"},
        {"id": 5, "name": "Отменена", "description": "Задача отменена"}
    ]

    existing_statuses = {s.id: s for s in session.query(TaskStatus).all()}

    for status in standard_statuses:
        if status["id"] not in existing_statuses:
            print(Fore.YELLOW + f"Добавление статуса задачи: {status['name']}")
            session.add(TaskStatus(id=status["id"], name=status["name"]))
        elif existing_statuses[status["id"]].name != status["name"]:
            existing_statuses[status["id"]].name = status["name"]
            print(Fore.YELLOW + f"Обновление статуса задачи: {status['name']}")

    session.commit()


def ensure_payment_statuses_exist(session) -> None:
    """
    Проверяет наличие стандартных статусов оплаты в базе данных, создает отсутствующие и обновляет описания.
    """
    standard_statuses = [
        {"id": 1, "name": "Нет оплаты", "description": "Задача не предполагает оплату"},
        {"id": 2, "name": "Возможна", "description": "Оплата возможна при качественном и своевременном выполнении"},
        {"id": 3, "name": "Начислена", "description": "Оплата начислена, но еще не выплачена"},
        {"id": 4, "name": "Оплачена", "description": "Задача оплачена полностью"}
    ]

    existing_statuses = {s.id: s for s in session.query(TaskPaymentStatus).all()}

    for status in standard_statuses:
        if status["id"] not in existing_statuses:
            print(Fore.YELLOW + f"Добавление статуса оплаты: {status['name']}")
            session.add(TaskPaymentStatus(id=status["id"], name=status["name"]))
        elif existing_statuses[status["id"]].name != status["name"]:
            existing_statuses[status["id"]].name = status["name"]
            print(Fore.YELLOW + f"Обновление статуса оплаты: {status['name']}")

    session.commit()


def import_order_comments_from_kis2() -> Dict[str, any]:
    """
    Импортирует комментарии к заказам из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_comments_list = create_order_comments_list_dict_from_kis2(debug=False)
        if not kis2_comments_list:
            print(Fore.YELLOW + "Не удалось получить комментарии к заказам из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_comments_list)} комментариев к заказам из КИС2.")
        with SyncSession() as session:
            try:
                # Создаем словарь для поиска людей по полному имени
                persons_by_name = {}
                for person in session.query(Person).all():
                    full_name = f"{person.surname} {person.name}"
                    if person.patronymic:
                        full_name += f" {person.patronymic}"
                    persons_by_name[full_name] = person.id

                # Получаем все записи из таблицы OrderComment
                comments = session.query(OrderComment).all()

                # Формируем множество уникальных значений момента создания заказа
                existing_comments_moment_of_creation_set = {
                    comment.moment_of_creation for comment in comments
                }
                for existing_comments_moment_of_creation in existing_comments_moment_of_creation_set:
                    print('existing_comments_moment_of_creation', existing_comments_moment_of_creation)

                existing_orders_set = {order.serial for order in session.query(Order).all()}
                print('existing_orders_set', existing_orders_set)

                # Обрабатываем каждый комментарий из КИС2
                for comment_data in kis2_comments_list:
                    order_serial = comment_data.get('order_serial')
                    person_name = comment_data.get('person')
                    text = comment_data.get('text', "")
                    moment_str = comment_data.get('moment_of_creation')

                    # Проверяем обязательные поля
                    if not order_serial or not person_name or not text:
                        print(Fore.YELLOW + f"Пропущен комментарий с неполными данными: {comment_data}")
                        continue

                    # Проверяем существование заказа
                    if order_serial not in existing_orders_set:
                        print(Fore.YELLOW + f"Не найден заказ '{order_serial}' для комментария. Пропуск.")
                        continue

                    # Ищем автора комментария
                    person_id = persons_by_name.get(person_name)
                    if not person_id:
                        print(Fore.YELLOW + f"Не найден человек '{person_name}' в базе данных. Пропуск комментария.")
                        continue

                    # Преобразуем строку даты в объект datetime
                    if moment_str:
                        try:
                            moment_of_creation = datetime.strptime(moment_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            print(Fore.YELLOW + f"Неверный формат даты '{moment_str}'. Используется текущее время.")
                            moment_of_creation = datetime.now()
                    else:
                        moment_of_creation = None

                    # Создаем ключ для проверки наличия комментария
                    comment_key = moment_of_creation
                    print('comment_key', comment_key)

                    # Проверяем существование комментария
                    if comment_key not in existing_comments_moment_of_creation_set:
                        # Создаем новый комментарий
                        new_comment = OrderComment(
                            order_id=order_serial,
                            person_id=person_id,
                            text=text,
                            moment_of_creation=moment_of_creation
                        )
                        session.add(new_comment)
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлен новый комментарий от {person_name} к заказу {order_serial}")
                    else:
                        result['unchanged'] += 1

                return commit_and_summarize_import(session, result, "комментариев к заказам")

            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте комментариев к заказам: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта комментариев к заказам: {e}")
        return result


def import_boxes_from_kis2() -> Dict[str, any]:
    """
    Импортирует корпуса шкафов из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_boxes_list = create_boxes_list_dict_from_kis2(debug=False)
        if not kis2_boxes_list:
            print(Fore.YELLOW + "Не удалось получить корпуса шкафов из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_boxes_list)} корпусов шкафов из КИС2.")
        with SyncSession() as session:
            try:
                # Получаем существующие корпуса шкафов
                existing_boxes = {b.vendor_code: b for b in session.query(ControlCabinet).all() if b.vendor_code}

                # Получаем ссылки на производителей
                manufacturers_dict = {name: id for id, name in session.query(Manufacturer.id,
                                                                             Manufacturer.name).all()}

                # Получаем ссылки на типы оборудования
                equipment_types_dict = {name: id for id, name in session.query(EquipmentType.id,
                                                                               EquipmentType.name).all()}

                # Получаем ссылки на валюты
                currencies_dict = {name: id for id, name in session.query(Currency.id, Currency.name).all()}

                # Получаем ссылки на материалы корпусов
                materials_dict = {name: id for id, name in session.query(ControlCabinetMaterial.id,
                                                                         ControlCabinetMaterial.name).all()}

                # Получаем ссылки на степени защиты IP
                ips_dict = {name: id for id, name in session.query(Ip.id, Ip.name).all()}

                # Проверяем, есть ли необходимые материалы и степени защиты
                # Если нет - создаем их
                unique_materials = set(item['material'] for item in kis2_boxes_list if 'material' in item)
                for material_name in unique_materials:
                    if material_name and material_name not in materials_dict:
                        print(Fore.YELLOW + f"Добавление нового материала корпуса: {material_name}")
                        new_material = ControlCabinetMaterial(name=material_name)
                        session.add(new_material)
                        session.flush()  # Чтобы получить id
                        materials_dict[material_name] = new_material.id

                unique_ips = set(item['ip'] for item in kis2_boxes_list if 'ip' in item)
                for ip_name in unique_ips:
                    if ip_name and ip_name not in ips_dict:
                        print(Fore.YELLOW + f"Добавление новой степени защиты IP: {ip_name}")
                        new_ip = Ip(name=ip_name)
                        session.add(new_ip)
                        session.flush()  # Чтобы получить id
                        ips_dict[ip_name] = new_ip.id

                # Убедимся, что в базе есть тип оборудования "Корпус шкафа"
                box_type_name = "Корпус шкафа"
                if box_type_name not in equipment_types_dict:
                    print(Fore.YELLOW + f"Добавление типа оборудования: {box_type_name}")
                    new_type = EquipmentType(name=box_type_name)
                    session.add(new_type)
                    session.flush()
                    equipment_types_dict[box_type_name] = new_type.id

                # Обрабатываем каждый корпус шкафа из КИС2
                for box_data in kis2_boxes_list:
                    name = box_data['equipment_name']
                    model = box_data.get('equipment_model')
                    vendor_code = box_data.get('vendor_code')
                    description = box_data.get('description', '')
                    manufacturer_name = box_data.get('manufacturer')
                    price = box_data.get('price')
                    currency_name = box_data.get('currency')
                    material_name = box_data.get('material')
                    ip_name = box_data.get('ip')
                    height = box_data.get('height')
                    width = box_data.get('width')
                    depth = box_data.get('depth')
                    relevance = box_data.get('relevance', True)
                    price_date = box_data.get('price_date')
                    if 'price_date' in box_data and box_data['price_date']:
                        try:
                            price_date = datetime.strptime(box_data['price_date'], "%Y-%m-%d").date()
                        except ValueError:
                            print(Fore.YELLOW + f"Неверный формат даты: {box_data['price_date']} для {name}")

                    # Проверяем наличие обязательных полей
                    if not vendor_code:
                        print(Fore.YELLOW + f"Пропущен корпус без артикула: {name}")
                        continue

                    # Проверяем наличие ссылок на связанные объекты
                    manufacturer_id = None
                    if manufacturer_name and manufacturer_name in manufacturers_dict:
                        manufacturer_id = manufacturers_dict[manufacturer_name]
                    elif manufacturer_name:
                        print(Fore.YELLOW + f"Производитель '{manufacturer_name}' не найден для корпуса {name}")

                    currency_id = None
                    if currency_name and currency_name in currencies_dict:
                        currency_id = currencies_dict[currency_name]
                    elif currency_name:
                        print(Fore.YELLOW + f"Валюта '{currency_name}' не найдена для корпуса {name}")

                    if material_name and material_name in materials_dict:
                        material_id = materials_dict[material_name]
                    else:
                        print(Fore.YELLOW + f"Материал '{material_name}' не найден для корпуса {name}. Пропуск.")
                        continue

                    if ip_name and ip_name in ips_dict:
                        ip_id = ips_dict[ip_name]
                    else:
                        print(Fore.YELLOW + f"Степень защиты IP '{ip_name}' не найдена для корпуса {name}. Пропуск.")
                        continue

                    # Если корпус уже существует по артикулу, обновляем его
                    if vendor_code in existing_boxes:
                        box = existing_boxes[vendor_code]
                        needs_update = False
                        update_details = []

                        # Проверяем изменения в основных полях
                        if box.name != name:
                            box.name = name
                            needs_update = True
                            update_details.append("название")
                        if box.model != model:
                            box.model = model
                            needs_update = True
                            update_details.append("модель")
                        if box.description != description:
                            box.description = description
                            needs_update = True
                            update_details.append("описание")
                        if box.manufacturer_id != manufacturer_id:
                            box.manufacturer_id = manufacturer_id
                            needs_update = True
                            update_details.append("производитель")
                        if box.price != price:
                            box.price = price
                            needs_update = True
                            update_details.append("цена")
                        if box.currency_id != currency_id:
                            box.currency_id = currency_id
                            needs_update = True
                            update_details.append("валюта")
                        if box.relevance != relevance:
                            box.relevance = relevance
                            needs_update = True
                            update_details.append("актуальность")
                        if box.price_date != price_date:
                            box.price_date = price_date
                            needs_update = True
                            update_details.append("дата цены")
                        if box.material_id != material_id:
                            box.material_id = material_id
                            needs_update = True
                            update_details.append("материал")
                        if box.ip_id != ip_id:
                            box.ip_id = ip_id
                            needs_update = True
                            update_details.append("степень защиты")
                        if box.height != height:
                            box.height = height
                            needs_update = True
                            update_details.append("высота")
                        if box.width != width:
                            box.width = width
                            needs_update = True
                            update_details.append("ширина")
                        if box.depth != depth:
                            box.depth = depth
                            needs_update = True
                            update_details.append("глубина")

                        if needs_update:
                            result['updated'] += 1
                            print(Fore.BLUE + f"Обновлен корпус '{vendor_code}': {', '.join(update_details)}")
                        else:
                            result['unchanged'] += 1
                    else:
                        # Создаем новый корпус шкафа
                        new_box = ControlCabinet(
                            name=name,
                            model=model,
                            vendor_code=vendor_code,
                            description=description,
                            type_id=equipment_types_dict.get(box_type_name),
                            manufacturer_id=manufacturer_id,
                            price=price,
                            currency_id=currency_id,
                            relevance=relevance,
                            price_date=datetime.strptime(price_date, "%Y-%m-%d").date(),
                            material_id=material_id,
                            ip_id=ip_id,
                            height=height,
                            width=width,
                            depth=depth
                        )
                        session.add(new_box)
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлен новый корпус: {vendor_code} - {name}")

                return commit_and_summarize_import(session, result, "корпусов шкафов")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте корпусов шкафов: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта корпусов шкафов: {e}")
        return result


def import_timings_from_kis2() -> Dict[str, any]:
    """
    Импортирует данные о затраченном времени (таймингах) из КИС2 в базу данных КИС3.
    """
    result = {"status": "error", "added": 0, "updated": 0, "unchanged": 0}
    try:
        kis2_timings_list = create_timings_list_dict_from_kis2(debug=False)
        if not kis2_timings_list:
            print(Fore.YELLOW + "Не удалось получить данные о таймингах из КИС2 или список пуст.")
            return result

        print(Fore.CYAN + f"Получено {len(kis2_timings_list)} записей о таймингах из КИС2.")
        with SyncSession() as session:
            try:
                # Создаем словарь для поиска людей по полному имени
                persons_by_name = {}
                for person in session.query(Person).all():
                    full_name = f"{person.surname} {person.name}"
                    if person.patronymic:
                        full_name += f" {person.patronymic}"
                    persons_by_name[full_name] = person.id

                # Проверяем существование заказов и задач
                existing_orders = set(serial[0] for serial in session.query(Order.serial).all())
                existing_tasks = set(id[0] for id in session.query(Task.id).all())

                # Получаем существующие тайминги для проверки дубликатов
                existing_timings = []
                for timing in session.query(Timing.order_serial, Timing.task_id, Timing.executor_id, Timing.timing_date).all():
                    existing_timings.append({
                        'order_serial': timing[0],
                        'task_id': timing[1],
                        'executor_id': timing[2],
                        'timing_date': timing[3]
                    })

                # Обрабатываем каждый тайминг из КИС2
                for timing_data in kis2_timings_list:
                    order_serial = timing_data.get('order_serial')
                    task_id = timing_data.get('task_id')
                    executor_name = timing_data.get('executor')
                    time_str = timing_data.get('time')
                    date_str = timing_data.get('date')

                    # Проверяем обязательные поля
                    if not order_serial or not task_id or not time_str:
                        print(Fore.YELLOW + f"Пропущен тайминг с неполными данными: {timing_data}")
                        continue

                    # Проверяем существование заказа
                    if order_serial not in existing_orders:
                        print(Fore.YELLOW + f"Не найден заказ '{order_serial}' для тайминга. Пропуск.")
                        continue

                    # Проверяем существование задачи
                    if task_id not in existing_tasks:
                        print(Fore.YELLOW + f"Не найдена задача с ID={task_id} для тайминга. Пропуск.")
                        continue

                    # Поиск исполнителя по имени
                    executor_id = None
                    if executor_name:
                        executor_id = persons_by_name.get(executor_name)
                        if not executor_id:
                            print(Fore.YELLOW + f"Не найден исполнитель '{executor_name}' в базе данных. "
                                                f"Тайминг будет привязан без исполнителя.")

                    # Преобразуем строку времени в timedelta
                    time_delta = parse_iso_duration(time_str)
                    if not time_delta:
                        print(Fore.YELLOW + f"Неверный формат времени '{time_str}' для тайминга. Пропуск.")
                        continue

                    # Преобразуем строку даты в объект date
                    timing_date = None
                    if date_str:
                        try:
                            timing_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except ValueError:
                            print(Fore.YELLOW + f"Неверный формат даты '{date_str}' для тайминга. Используем None.")

                    # Проверяем, существует ли тайминг с такими же параметрами
                    is_duplicate = False
                    for existing in existing_timings:
                        if (existing['order_serial'] == order_serial and
                            existing['task_id'] == task_id and
                            existing['executor_id'] == executor_id and
                            existing['timing_date'] == timing_date):
                            is_duplicate = True
                            result['unchanged'] += 1
                            break

                    if not is_duplicate:
                        # Создаем новый тайминг
                        new_timing = Timing(
                            order_serial=order_serial,
                            task_id=task_id,
                            executor_id=executor_id,
                            time=time_delta,
                            timing_date=timing_date
                        )
                        session.add(new_timing)
                        result['added'] += 1
                        print(Fore.GREEN + f"Добавлен новый тайминг: Заказ {order_serial}, Задача {task_id}, "
                                           f"Исполнитель {executor_name}, Время {time_str}, Дата {date_str}")

                return commit_and_summarize_import(session, result, "записей о затраченном времени")
            except Exception as e:
                session.rollback()
                print(Fore.RED + f"Ошибка при импорте таймингов: {e}")
                return result
    except Exception as e:
        print(Fore.RED + f"Ошибка при выполнении импорта таймингов: {e}")
        return result


if __name__ == "__main__":
    def print_import_results(import_result, entity_name):
        """
        Выводит результаты импорта в консоль с форматированием.
        """
        if import_result['status'] == 'success':
            result_messages = []
            if import_result.get('added', 0) > 0:
                result_messages.append(f"добавлено: {import_result['added']}")
            if import_result.get('updated', 0) > 0:
                result_messages.append(f"обновлено: {import_result['updated']}")
            if import_result.get('unchanged', 0) > 0:
                result_messages.append(f"без изменений: {import_result['unchanged']}")
            total = import_result.get('added', 0) + import_result.get('updated', 0) + import_result.get('unchanged', 0)
            if import_result.get('added', 0) > 0 or import_result.get('updated', 0) > 0:
                print(Fore.GREEN + f"Результат импорта {entity_name} ({total}): {', '.join(result_messages)}")
            else:
                print(Fore.YELLOW + f"{entity_name.capitalize()} обработаны ({total}): {', '.join(result_messages)}")
        else:
            print(Fore.RED + f"Ошибка при импорте {entity_name}.")


    answer = ""
    while answer != "e":
        print("\nChange action:")
        print("e - exit")
        print("1 - copy countries from KIS2")
        print("2 - copy manufacturers from KIS2")
        print("3 - copy equipment types from KIS2")
        print("4 - copy currencies from KIS2")
        print("5 - copy cities from KIS2")
        print("6 - copy counterparty forms from KIS2")
        print("7 - copy companies from KIS2")
        print("8 - copy people from KIS2")
        print("9 - copy works from KIS2")
        print("10 - ensure order statuses exist")
        print("11 - import orders from KIS2")
        print("12 - import box accounting from KIS2")
        print("13 - import tasks from KIS2")
        print("14 - import order comments from KIS2")
        print("15 - import box from KIS2")
        print("16 - import timings from KIS2")
        answer = input()

        operations = {
            "1": ("Импорт стран из КИС2", import_countries_from_kis2, "стран"),
            "2": ("Импорт производителей из КИС2", import_manufacturers_from_kis2, "производителей"),
            "3": ("Импорт типов оборудования из КИС2", import_equipment_type_from_kis2, "типов оборудования"),
            "4": ("Импорт валют из КИС2", import_currency_from_kis2, "валют"),
            "5": ("Импорт городов из КИС2", import_cities_from_kis2, "городов"),
            "6": ("Импорт форм контрагентов из КИС2", import_counterparty_from_kis2, "форм контрагентов"),
            "7": ("Импорт компаний из КИС2", import_companies_from_kis2, "компаний"),
            "8": ("Импорт людей из КИС2", import_person_from_kis2, "людей"),
            "9": ("Импорт работ из КИС2", import_works_from_kis2, "работ"),
            "10": ("Проверка и создание стандартных статусов заказов", ensure_order_statuses_exist, "статусов заказов"),
            "11": ("Импорт заказов из КИС2", import_orders_from_kis2, "заказов"),
            "12": ("Импорт учёта шкафов из КИС2", import_box_accounting_from_kis2, "учёта шкафов"),
            "13": ("Импорт задач из КИС2", import_tasks_from_kis2, "задач"),
            "14": ("Импорт комментариев заказов из КИС2", import_order_comments_from_kis2, "комментариев к заказам"),
            "15": ("Импорт корпусов шкафов из КИС2", import_boxes_from_kis2, "корпусов шкафов"),
            "16": ("Импорт расписаний из КИС2", import_timings_from_kis2, "расписаний"),
        }

        if answer in operations:
            if test_sync_connection():
                try:
                    title, func, entity_name = operations[answer]
                    print(Fore.CYAN + f"=== {title} ===")
                    import_result = func()
                    print_import_results(import_result, entity_name)
                except Exception as e:
                    print(Fore.RED + f"Ошибка при выполнении операции: {e}")
            else:
                print(Fore.RED + "Операции с данными не выполнены: нет подключения к базе данных.")
        elif answer != "e":
            print(Fore.RED + "Неверный ввод. Повторите попытку.")

    print("Goodbye!")
