# utils/import_data.py
"""
Модуль импорта данных из КИС2(БД SQlite3) в КИС3(БД PostgreSQL).
Получение данных из КИС2(БД SQlite3) реализовано через Django Rest API.
"""
import sys
import os
from datetime import datetime

from colorama import init, Fore
from typing import Dict, Set, Any

# Добавляем родительскую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Игнорирование ошибки PEP 8: E402 для импортов, требующих модификации sys.path
# pylint: disable=E402
from kis2.DjangoRestAPI import create_countries_set_from_kis2
from kis2.DjangoRestAPI import create_companies_list_dict_from_kis2
from kis2.DjangoRestAPI import create_list_dict_manufacturers
from kis2.DjangoRestAPI import create_equipment_type_set_from_kis2
from kis2.DjangoRestAPI import create_money_set_from_kis2
from kis2.DjangoRestAPI import create_cities_set_from_kis2
from kis2.DjangoRestAPI import create_companies_form_from_kis2
from kis2.DjangoRestAPI import create_person_list_dict_from_kis2
from kis2.DjangoRestAPI import create_works_list_dict_from_kis2
from kis2.DjangoRestAPI import create_orders_list_dict_from_kis2

from database import SyncSession, test_sync_connection
from models.models import Country
from models.models import Manufacturer
from models.models import Counterparty
from models.models import CounterpartyForm
from models.models import City
from models.models import OrderStatus
from models.models import EquipmentType
from models.models import Currency
from models.models import Person
from models.models import Work
from models.models import Order
# pylint: enable=E402

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
            "11": ("Импорт заказов из КИС2", import_orders_from_kis2, "заказов")
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
