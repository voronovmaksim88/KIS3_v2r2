# kis2/DjangoRestAPI.py
"""
Модуль для работы с API КИС2 с использованием Django Rest Framework.
"""

import requests
import re
import json
from typing import Dict, List, Set, Optional, Any


def _create_authenticated_session(
        base_url: str,
        username: str,
        password: str,
        debug: bool = False) -> Optional[requests.Session]:
    """
    Создает и авторизует сессию для работы с API КИС2.
    
    Args:
        base_url: Базовый URL КИС2
        username: Имя пользователя
        password: Пароль
        debug: Режим отладки
        
    Returns:
        Аутентифицированная сессия или None в случае ошибки
    """
    login_url = f"{base_url}/accounts/login/"
    session = requests.Session()

    try:
        # Получаем страницу логина для получения CSRF токена
        login_page = session.get(login_url)

        if debug:
            print(f"Получение страницы логина: {login_page.status_code}")

        # Находим CSRF токен в HTML-странице
        if 'csrfmiddlewaretoken' in login_page.text:
            csrf_token = re.search('name="csrfmiddlewaretoken" value="(.+?)"', login_page.text).group(1)
            if debug:
                print(f"CSRF Token из HTML: {csrf_token}")
        else:
            csrf_token = session.cookies.get('csrftoken')
            if debug:
                print(f"CSRF Token из cookies: {csrf_token}")

        # Данные для логина
        login_data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token,
        }

        # Заголовки для отправки CSRF токена
        headers = {
            'Referer': login_url,
        }

        # Выполняем вход
        login_response = session.post(login_url, data=login_data, headers=headers)

        if debug:
            print(f"Статус входа (200 - это успешно): {login_response.status_code}")
            print(f"Редирект URL: {login_response.url}")

        # Проверяем успешность входа
        if '/login/' in login_response.url:
            print("Не удалось войти, проверьте логин и пароль")
            return None

        return session

    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP запроса при аутентификации: {e}")
        return None
    except Exception as e:
        print(f"Непредвиденная ошибка при аутентификации: {e}")
        return None


def _make_api_request(session: requests.Session, api_url: str, debug: bool = False) -> Optional[Any]:
    """
    Выполняет API запрос и обрабатывает ответ.
    
    Args:
        session: Аутентифицированная сессия
        api_url: URL API запроса
        debug: Режим отладки
        
    Returns:
        Данные ответа API или None в случае ошибки
    """
    # Инициализируем переменную перед блоком try
    api_response = None

    try:
        # Выполняем запрос
        api_response = session.get(api_url)

        if debug:
            print(f"Статус API запроса: {api_response.status_code}")
            print(f"Content-Type: {api_response.headers.get('Content-Type', '')}")

        # Проверяем успешность запроса
        api_response.raise_for_status()

        # Проверяем, что получили JSON, а не HTML
        if 'text/html' in api_response.headers.get('Content-Type', ''):
            print("Получен HTML вместо JSON, возможно, авторизация не сработала")
            if debug:
                print(f"Полный ответ: {api_response.text}")
            return None

        # Парсин JSON
        data = api_response.json()

        if debug:
            pretty_json = json.dumps(data, ensure_ascii=False, indent=2)
            print(f"Читаемый ответ API: {pretty_json[:500]}...")

        return data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP запроса при API запросе: {e}")
        return None
    except ValueError as e:
        print(f"Ошибка при разборе JSON: {e}")
        if debug and api_response is not None:
            print(f"Текст ответа: {api_response.text}")
        return None
    except Exception as e:
        print(f"Непредвиденная ошибка при API запросе: {e}")
        return None


def get_data_from_kis2(endpoint: str, debug: bool = False) -> Optional[List[Dict]]:
    """
    Получает данные из API КИС2 для указанного эндпоинта.
    
    Args:
        endpoint: Эндпоинт API без слеша в начале (например "Countries")
        debug: Режим отладки
        
    Returns:
        Список словарей с данными или None в случае ошибки
    """
    base_url = "https://kis2test.sibplc.ru"
    username = "admin"
    password = "djangoadmin"
    api_url = f"{base_url}/api/{endpoint}/"

    # Создаем аутентифицированную сессию
    session = _create_authenticated_session(base_url, username, password, debug)
    if not session:
        return None

    # Выполняем API запрос
    data = _make_api_request(session, api_url, debug)

    # Проверяем, что данные имеют ожидаемую структуру
    if data is not None and not isinstance(data, list):
        print(f"Ожидался список, но получен: {type(data)}")
        return None

    return data


def get_entity_dict(entity_name: str, name_field: str = "name",
                    default_value: str = "Неизвестно", debug: bool = True) -> Dict[Any, str]:
    """
    Получает данные о сущностях и создает словарь id:name

    Args:
        entity_name: Имя сущности для запроса
        name_field: Поле, содержащее название (по умолчанию "name")
        default_value: Значение по умолчанию если name_field отсутствует
        debug: Флаг для вывода отладочной информации

    Returns:
        Словарь, где ключ - id сущности, значение - название
    """
    data = get_data_from_kis2(entity_name, debug)
    if not data:
        if debug:
            print(f"Не удалось получить данные о {entity_name}")
        return {}

    # Создаем словарь id:name для сущностей
    entity_dict = {item["id"]: item.get(name_field, default_value)
                   for item in data
                   if "id" in item}

    if debug:
        print(f"Получено {len(entity_dict)} записей {entity_name}")

    return entity_dict


def get_currencies_dict(debug=False):
    """
    Получает данные о валютах из KIS2 и создает словарь идентификаторов и имен валют.

    Args:
        debug (bool): Флаг для включения отладочной информации

    Returns:
        dict: Словарь в формате {id: name} для валют
    """
    # Получаем данные о валютах
    currencies_data = get_data_from_kis2("Money", debug)

    if not currencies_data:
        if debug:
            print("Не удалось получить данные о валютах")
        return {}

    # Создаем словарь id:name для валют
    currencies_dict = {item["id"]: item["name"]
                       for item in currencies_data
                       if "id" in item and "name" in item}

    if debug:
        print(f"Получено {len(currencies_dict)} валют")

    return currencies_dict


def get_persons_dict(debug: bool = True) -> Dict[Any, str]:
    """
    Получает данные о сотрудниках и создает словарь id:полное_имя

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Словарь, где ключ - id сотрудника, значение - полное ФИО
    """
    persons_data = get_data_from_kis2("Person", debug)
    if not persons_data:
        if debug:
            print("Не удалось получить данные о сотрудниках")
        return {}

    # Создаем словарь id:полное_имя для сотрудников
    persons_dict = {}
    for person in persons_data:
        if "id" in person:
            # Формируем полное ФИО из фамилии, имени и отчества
            surname = person.get("surname", "")
            name = person.get("name", "")
            patronymic = person.get("patronymic", "")

            # Собираем ФИО в одну строку, пропуская пустые значения
            full_name_parts = [part for part in [surname, name, patronymic] if part]
            full_name = " ".join(full_name_parts) if full_name_parts else "Неизвестный сотрудник"

            persons_dict[person["id"]] = full_name

    if debug:
        print(f"Получено {len(persons_dict)} сотрудников")

    return persons_dict


def create_countries_set_from_kis2(debug: bool = True) -> Set[str]:
    """
    Получает множество названий стран из КИС2.
    
    Args:
        debug: Режим отладки
        
    Returns:
        Множество названий стран
    """
    countries_data = get_data_from_kis2("Countries", debug)

    if not countries_data:
        return set()

    # Создаем множество из названий стран
    countries_set = {item["name"] for item in countries_data if "name" in item}

    if debug:
        print(f"Получено {len(countries_set)} стран")

    return countries_set


def create_list_dict_manufacturers(debug: bool = True) -> List[Dict[str, str]]:
    """
    Получает список производителей из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации
        
    Returns:
        Список словарей производителей.
        Каждый словарь содержит ключ 'name'-название производителя, ключ 'country' - название страны
        Например - [{'name':'Zentec', country:'Россия'}, {'name':'Segnetics', country:'Россия'}].
    """
    # Получаем данные о странах
    countries_data = get_data_from_kis2("Countries", debug)
    if not countries_data:
        return []

    # Создаем словарь id:name для стран
    countries_dict = {item["id"]: item["name"] for item in countries_data if "id" in item and "name" in item}

    if debug:
        print(f"Получено {len(countries_dict)} стран")

    # Получаем данные о производителях
    manufacturers_data = get_data_from_kis2("Manufacturers", debug)
    if not manufacturers_data:
        return []

    if debug:
        print('manufacturers_data', manufacturers_data)

    # Создаем список словарей производителей
    manufacturers_list = []
    for manufacturer in manufacturers_data:
        # Проверяем наличие необходимых ключей
        if "name" in manufacturer and "country_id" in manufacturer:
            country_id = manufacturer["country_id"]
            country_name = countries_dict.get(country_id, "Неизвестная страна")

            manufacturers_list.append({
                'name': manufacturer["name"],
                'country': country_name
            })

            if debug:
                print(f"Добавлен производитель: {manufacturer['name']} из страны {country_name}")

    if debug:
        print(f"Получено {len(manufacturers_list)} производителей")

    return manufacturers_list


def create_equipment_type_set_from_kis2(debug: bool = True) -> Set[str]:
    """
    Получает множество названий типов оборудования из КИС2.

    Args:
        debug: Режим отладки

    Returns:
        Множество названий типов оборудования
    """
    equipment_types_data = get_data_from_kis2("EquipmentType", debug)

    if not equipment_types_data:
        return set()

    # Создаем множество из названий типов оборудования
    equipment_types_set = {item["name"] for item in equipment_types_data if "name" in item}

    if debug:
        print(f"Получено {len(equipment_types_set)} типов оборудования")

    return equipment_types_set


def create_money_set_from_kis2(debug: bool = True) -> Set[str]:
    """
    Получает множество названий валют из КИС2.

    Args:
        debug: Режим отладки

    Returns:
        Множество названий валют
    """
    moneys_data = get_data_from_kis2("Money", debug)

    if not moneys_data:
        return set()

    # Создаем множество из названий валют
    moneys_set = {item["name"] for item in moneys_data if "name" in item}

    if debug:
        print(f"Получено {len(moneys_set)} валют")

    return moneys_set


def create_cities_set_from_kis2(debug: bool = True) -> Set[str]:
    """
    Получает множество названий городов из КИС2.

    Args:
        debug: Режим отладки

    Returns:
        Множество названий городов
    """
    cities_data = get_data_from_kis2("City", debug)

    if not cities_data:
        return set()

    # Создаем множество из названий городов
    cities_set = {item["name"] for item in cities_data if "name" in item}

    if debug:
        print(f"Получено {len(cities_set)} городов")

    return cities_set


def create_companies_form_from_kis2(debug: bool = True) -> Set[str]:
    """
    Получает множество форм компаний из КИС2.

    Args:
        debug: Режим отладки

    Returns:
        Множество названий форм компаний
    """
    companies_form_data = get_data_from_kis2("CompaniesForm", debug)

    if not companies_form_data:
        return set()

    # Создаем множество из названий городов
    companies_form_set = {item["name"] for item in companies_form_data if "name" in item}

    if debug:
        print(f"Получено {len(companies_form_set)} форм контрагентов")

    return companies_form_set


def create_companies_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей компаний из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей компаний со следующими ключами:
        - 'name': Название компании
        - 'form': Название формы компании (ООО, ИП, и т.д.)
        - 'note': Примечание к компании (может быть None)
        - 'city': Название города (может быть None)
    """
    # Получаем данные о формах компаний
    company_forms_data = get_data_from_kis2("CompaniesForm", debug)
    if not company_forms_data:
        if debug:
            print("Не удалось получить данные о формах компаний")
        return []

    # Создаем словарь id:name для форм компаний
    company_forms_dict = {item["id"]: item["name"]
                          for item in company_forms_data
                          if "id" in item and "name" in item}

    if debug:
        print(f"Получено {len(company_forms_dict)} форм компаний")

    # Получаем данные о городах
    cities_data = get_data_from_kis2("City", debug)
    if not cities_data:
        if debug:
            print("Не удалось получить данные о городах")
        return []

    # Создаем словарь id:name для городов
    cities_dict = {item["id"]: item["name"]
                   for item in cities_data
                   if "id" in item and "name" in item}

    if debug:
        print(f"Получено {len(cities_dict)} городов")

    # Получаем данные о компаниях
    companies_data = get_data_from_kis2("Company", debug)
    if not companies_data:
        if debug:
            print("Не удалось получить данные о компаниях")
        return []

    # Создаем список словарей компаний
    companies_list = []
    for company in companies_data:
        # Проверяем наличие необходимых ключей
        if "name" in company:
            # Получаем форму компании если указана
            form_id = company.get("form_id")
            form_name = company_forms_dict.get(form_id, None) if form_id else None

            # Получаем город если указан
            city_id = company.get("city_id")
            city_name = cities_dict.get(city_id, None) if city_id else None

            # Собираем словарь компании
            company_dict = {
                'name': company["name"],
                'form': form_name,
                'note': company.get("note"),  # может быть None
                'city': city_name  # может быть None
            }

            companies_list.append(company_dict)

            if debug:
                print(f"Добавлена компания: {company['name']}")

    if debug:
        print(f"Получено {len(companies_list)} компаний")

    return companies_list


def create_person_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей людей из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей людей со следующими ключами:
        - 'name': Имя
        - 'patronymic': Отчество
        - 'surname': Фамилия
        - 'phone': Телефон
        - 'email': Email
        - 'company': Название компании (может быть None)
    """
    # Получаем данные о компаниях
    companies_data = get_data_from_kis2("Company", debug)
    if not companies_data:
        if debug:
            print("Не удалось получить данные о компаниях")
        return []

    # Создаем словарь id:name для компаний
    companies_dict = {item["id"]: item["name"]
                      for item in companies_data
                      if "id" in item and "name" in item}

    if debug:
        print(f"Получено {len(companies_dict)} компаний")

    # Получаем данные о людях
    persons_data = get_data_from_kis2("Person", debug)
    if not persons_data:
        if debug:
            print("Не удалось получить данные о людях")
        return []

    # Создаем список словарей людей
    persons_list = []
    for person in persons_data:
        # Проверяем наличие необходимых ключей
        if "name" in person and "surname" in person:
            # Получаем компанию, если указана
            company_id = person.get("company_id")
            company_name = companies_dict.get(company_id, None) if company_id else None

            # Собираем словарь человека
            person_dict = {
                'name': person.get("name"),
                'patronymic': person.get("patronymic"),
                'surname': person.get("surname"),
                'phone': person.get("phone"),
                'email': person.get("email"),
                'company': company_name  # может быть None
            }

            persons_list.append(person_dict)

            if debug:
                print(f"Добавлен человек: {person['surname']} {person['name']}")

    if debug:
        print(f"Получено {len(persons_list)} людей")

    return persons_list


def create_works_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей работ из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей работ со следующими ключами:
        - 'name': Название работы
        - 'description': Описание работы
    """
    # Получаем данные о работах
    works_data = get_data_from_kis2("Work", debug)
    if not works_data:
        if debug:
            print("Не удалось получить данные о работах")
        return []

    # Создаем список словарей работ
    works_list = []
    for work in works_data:
        # Проверяем наличие необходимых ключей
        if "name" in work:
            # Собираем словарь работы
            work_dict = {
                'name': work["name"],
                'description': work.get("description", "")  # может быть пустой строкой
            }

            works_list.append(work_dict)

            if debug:
                print(f"Добавлена работа: {work['name']}")

    if debug:
        print(f"Получено {len(works_list)} работ")

    return works_list


def get_order_status(status_id: Optional[int]) -> str:
    """
    Возвращает статус заказа текстом по его id.
    """
    if status_id == 0:
        return 'Не определён'
    elif status_id == 1:
        return 'На согласовании'
    elif status_id == 2:
        return 'На согласовании'
    elif status_id == 3:
        return 'В работе'
    elif status_id == 4:
        return 'Выполнено в срок'
    elif status_id == 5:
        return 'Выполнено НЕ в срок'
    elif status_id == 6:
        return 'Не согласовано'
    elif status_id == 7:
        return 'На паузе'
    else:
        return 'Неизвестный статус'


def create_orders_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Получает список заказов из КИС2 через REST API и преобразует их в список словарей.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей заказов со следующими ключами:
        - 'serial': Серийный номер заказа (формат NNN-MM-YYYY)
        - 'name': Название заказа
        - 'customer': Название компании-заказчика
        - 'priority': Приоритет заказа (1-10)
        - 'status': Статус заказа текстом
        - 'start_moment': Дата и время создания заказа
        - 'dedline_moment': Крайний срок завершения
        - 'end_moment': Фактический срок завершения
        - 'works': Список названий работ по заказу
        - 'materialsCost': Стоимость материалов
        - 'materialsPaid': Материалы оплачены (True/False)
        - 'productsCost': Стоимость товаров
        - 'productsPaid': Товары оплачены (True/False)
        - 'workCost': Стоимость работ
        - 'workPaid': Работы оплачены (True/False)
        - 'debt': Задолженность
        - 'debtPaid': Задолженность оплачена (True/False)
    """
    # Получаем данные о компаниях
    companies_data = get_data_from_kis2("Company", debug)
    if not companies_data:
        if debug:
            print("Не удалось получить данные о компаниях")
        companies_dict = {}
    else:
        # Создаем словарь id:name для компаний
        companies_dict = {item["id"]: item["name"] for item in companies_data if "id" in item and "name" in item}
        if debug:
            print(f"Получено {len(companies_dict)} компаний")

    # Получаем данные о работах
    works_data = get_data_from_kis2("Work", debug)
    if not works_data:
        if debug:
            print("Не удалось получить данные о работах")
        works_dict = {}
    else:
        # Создаем словарь id:name для работ
        works_dict = {item["id"]: item["name"] for item in works_data if "id" in item and "name" in item}
        if debug:
            print(f"Получено {len(works_dict)} работ")

    # Получаем данные о заказах
    orders_data = get_data_from_kis2("Order", debug)
    if not orders_data:
        if debug:
            print("Не удалось получить данные о заказах")
        return []

    # Создаем список словарей заказов
    orders_list = []
    for order in orders_data:
        # Проверяем наличие обязательного ключа
        if "serial" not in order:
            if debug:
                print(f"Пропущен заказ без серийного номера: {order}")
            continue

        # Получаем название компании-заказчика
        customer_name = None
        if "customer_id" in order and order["customer_id"] in companies_dict:
            customer_name = companies_dict[order["customer_id"]]

        # Получаем список названий работ
        works_list = []
        if "works" in order and isinstance(order["works"], list):
            for work_id in order["works"]:
                if work_id in works_dict:
                    works_list.append(works_dict[work_id])

        # Формируем словарь заказа
        order_dict = {
            'serial': order["serial"],
            'name': order.get("name", ""),
            'customer': customer_name,
            'priority': order.get("priority"),
            'status': get_order_status(order.get("status")),
            'start_moment': order.get("start_moment"),
            'dedline_moment': order.get("dedline_moment"),
            'end_moment': order.get("end_moment"),
            'works': works_list,
            'materialsCost': order.get("materialsCost", 0),
            'materialsPaid': order.get("materialsPaid", False),
            'productsCost': order.get("productsCost", 0),
            'productsPaid': order.get("productsPaid", False),
            'workCost': order.get("workCost", 0),
            'workPaid': order.get("workPaid", False),
            'debt': order.get("debt", 0),
            'debtPaid': order.get("debtPaid", False)
        }

        orders_list.append(order_dict)

        if debug:
            print(f"Добавлен заказ: {order['serial']} - {order.get('name', 'Без названия')}")

    if debug:
        print(f"Всего получено {len(orders_list)} заказов")

    return orders_list


def create_box_accounting_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей шкафов (Box_Accounting) из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей шкафов со следующими ключами:
        - 'serial_num': Серийный номер шкафа
        - 'name': Название шкафа
        - 'order': Заказ (серийный номер заказа)
        - 'scheme_developer': Разработчик схемы (ФИО одной строкой)
        - 'assembler': Сборщик (ФИО одной строкой)
        - 'programmer': Программист (ФИО одной строкой, может быть None)
        - 'tester': Тестировщик (ФИО одной строкой)
    """
    # Получаем словари для поиска
    # orders_dict = get_entity_dict("Order", "serial", "Неизвестный заказ", debug)
    persons_dict = get_persons_dict(debug)

    # Получаем данные о шкафах
    boxes_data = get_data_from_kis2("Box_Accounting", debug)
    if not boxes_data:
        if debug:
            print("Не удалось получить данные о шкафах")
        return []

    # Создаем список словарей шкафов
    boxes_list = []
    for box in boxes_data:
        # Проверяем наличие необходимых ключей
        if "serial_num" in box and "name" in box:
            # Получаем информацию о заказе
            order_serial = box.get("order_id")

            # Получаем информацию о разработчике схемы
            scheme_developer_id = box.get("scheme_developer_id")
            scheme_developer_name = persons_dict.get(scheme_developer_id, None) if scheme_developer_id else None

            # Получаем информацию о сборщике
            assembler_id = box.get("assembler_id")
            assembler_name = persons_dict.get(assembler_id, None) if assembler_id else None

            # Получаем информацию о программисте (может быть None)
            programmer_id = box.get("programmer_id")
            programmer_name = persons_dict.get(programmer_id, None) if programmer_id else None

            # Получаем информацию о тестировщике
            tester_id = box.get("tester_id")
            tester_name = persons_dict.get(tester_id, None) if tester_id else None

            # Собираем словарь шкафа
            box_dict = {
                'serial_num': box["serial_num"],
                'name': box["name"],
                'order_serial': order_serial,
                'scheme_developer': scheme_developer_name,
                'assembler': assembler_name,
                'programmer': programmer_name,
                'tester': tester_name
            }

            boxes_list.append(box_dict)

            if debug:
                print(f"Добавлен шкаф: {box['name']} (S/N: {box['serial_num']})")

    if debug:
        print(f"Получено {len(boxes_list)} шкафов")

    return boxes_list


def create_tasks_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей задач (Task) из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей задач со следующими ключами:
        - 'name': Название задачи
        - 'executor': Исполнитель задачи (ФИО одной строкой)
        - 'planned_duration': Планируемая продолжительность выполнения задачи
        - 'actual_duration': Фактическая продолжительность выполнения задачи
        - 'creation_moment': Дата и время создания задачи
        - 'start_moment': Дата и время начала выполнения задачи
        - 'end_moment': Дата и время завершения выполнения задачи
        - 'status': Статус выполнения задачи
        - 'cost': Стоимость выполнения задачи
        - 'payment_status': Статус оплаты за задачу
        - 'root_task': ID корневой задачи
        - 'parent_task': ID родительской задачи
        - 'description': Описание задачи
    """
    # Получаем словари для поиска
    persons_dict = get_persons_dict(debug)

    # Получаем данные о статусах задач
    task_statuses_data = get_data_from_kis2("TaskStatus", debug)
    if not task_statuses_data:
        if debug:
            print("Не удалось получить данные о статусах задач")
        return []

    # Создаем словарь id:name для статусов задач
    task_statuses_dict = {status["id"]: status.get("name", "Неизвестный статус")
                          for status in task_statuses_data
                          if "id" in status}

    if debug:
        print(f"Получено {len(task_statuses_dict)} статусов задач")

    # Получаем данные о статусах оплаты
    payment_statuses_data = get_data_from_kis2("PaymentStatus", debug)
    if not payment_statuses_data:
        if debug:
            print("Не удалось получить данные о статусах оплаты")
        return []

    # Создаем словарь id:name для статусов оплаты
    payment_statuses_dict = {status["id"]: status.get("name", "Неизвестный статус оплаты")
                             for status in payment_statuses_data
                             if "id" in status}

    if debug:
        print(f"Получено {len(payment_statuses_dict)} статусов оплаты")

    # Получаем данные о задачах
    tasks_data = get_data_from_kis2("Task", debug)
    if not tasks_data:
        if debug:
            print("Не удалось получить данные о задачах")
        return []

    # Создаем список словарей задач
    tasks_list = []
    for task in tasks_data:
        # Проверяем наличие необходимого ключа name
        if "name" in task:
            # Получаем информацию об исполнителе
            executor_id = task.get("executor_id")
            executor_name = persons_dict.get(executor_id, None) if executor_id else None

            # Получаем информацию о статусе задачи
            status_id = task.get("status_id")
            status_name = task_statuses_dict.get(status_id, None) if status_id else None

            # Получаем информацию о статусе оплаты
            payment_status_id = task.get("payment_status_id")
            payment_status_name = payment_statuses_dict.get(payment_status_id, None) if payment_status_id else None

            # Получаем информацию о корневой задаче
            root_task_id = task.get("root_task_id")

            # Получаем информацию о родительской задаче
            parent_task_id = task.get("parent_task_id")

            # Собираем словарь задачи
            task_dict = {
                'id': task.get("id"),
                'name': task["name"],
                'executor': executor_name,  # Используем ФИО вместо ID исполнителя
                'order_id': task.get("order_id"),  # Добавлено поле order_id
                'planned_duration': task.get("planned_duration"),
                'actual_duration': task.get("actual_duration"),
                'creation_moment': task.get("creation_moment"),
                'start_moment': task.get("start_moment"),
                'end_moment': task.get("end_moment"),
                'status': status_name,
                'cost': task.get("cost"),
                'payment_status': payment_status_name,
                'root_task_id': root_task_id,
                'parent_task_id': parent_task_id,
                'description': task.get("description")
            }
            tasks_list.append(task_dict)

            if debug:
                print(f"Добавлена задача: {task['name']} (ID: {task.get('id')}, Исполнитель: {executor_name})")

    if debug:
        print(f"Получено {len(tasks_list)} задач")

    return tasks_list


def create_order_comments_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей комментариев к заказам (OrderComent) из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей комментариев со следующими ключами:
        - 'moment_of_creation': Дата и время публикации комментария
        - 'text': Текст комментария
        - 'person': ФИО автора комментария (одной строкой)
        - 'order_serial': Серийный номер заказа, к которому относится комментарий
    """
    # Получаем словари для поиска
    persons_dict = get_persons_dict(debug)

    # Получаем данные о комментариях
    comments_data = get_data_from_kis2("OrderComent", debug)
    if not comments_data:
        if debug:
            print("Не удалось получить данные о комментариях к заказам")
        return []

    # Создаем список словарей комментариев
    comments_list = []
    for comment in comments_data:
        # Проверяем наличие необходимых ключей
        if "text" in comment:
            # Получаем информацию об авторе комментария
            person_id = comment.get("person_id")
            person_name = persons_dict.get(person_id, None) if person_id else None

            # Получаем информацию о заказе
            order_serial = comment.get("order_id")

            # Собираем словарь комментария
            comment_dict = {
                'moment_of_creation': comment.get("moment_of_creation"),
                'text': comment["text"],
                'person': person_name,
                'order_serial': order_serial
            }

            comments_list.append(comment_dict)

            if debug:
                text_preview = comment["text"][:50] + "..." if len(comment["text"]) > 50 else comment["text"]
                print(f"Добавлен комментарий: '{text_preview}' (Автор: {person_name}, Заказ: {order_serial})")

    if debug:
        print(f"Получено {len(comments_list)} комментариев к заказам")

    return comments_list


def create_timings_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей записей о потраченном времени (Timing) из КИС2 через REST API.
    Args:
        debug: Флаг для вывода отладочной информации
    Returns:
        Список словарей записей о потраченном времени со следующими ключами:
        - 'order_serial': Серийный номер заказа
        - 'task_id': ID задачи
        - 'executor': Исполнитель (ФИО одной строкой)
        - 'time': Потраченное время в формате ISO 8601 (например, "PT5H30M")
        - 'date': Дата тайминга
    """
    # Получаем необходимые справочники
    persons_dict = get_persons_dict(debug)  # Словарь ID:ФИО сотрудников

    # Получаем данные о таймингах
    timings_data = get_data_from_kis2("Timing", debug)
    if not timings_data:
        if debug:
            print("Не удалось получить данные о потраченном времени")
        return []

    # Создаем список словарей таймингов
    timings_list = []
    for timing in timings_data:
        # Проверяем наличие необходимых ключей
        if "order_id" in timing and "task_id" in timing:
            # Получаем информацию о заказе
            order_serial = timing["order_id"]
            # Вместо имени задачи используем только ID
            task_id = timing.get("task_id")
            # Получаем информацию об исполнителе
            executor_id = timing.get("executor_id")
            executor_name = persons_dict.get(executor_id, "Неизвестный исполнитель")  # Преобразуем ID в ФИО
            # Конвертируем время в формат ISO 8601
            time_spent = timing.get("time")
            if time_spent:
                # Используем регулярное выражение для извлечения часов, минут и секунд
                match = re.match(r"P(\d+)DT(\d+)H(\d+)M(\d+)S", time_spent)
                if match:
                    days, hours, minutes, seconds = map(int, match.groups())
                    total_hours = days * 24 + hours  # Переводим дни в часы
                    # Формируем строку в формате ISO 8601 для интервала времени
                    time_iso = f"PT{total_hours}H{minutes}M"
                else:
                    # Если формат не соответствует ожидаемому, возвращаем нулевой интервал
                    print(f"Неподдерживаемый формат времени: {time_spent}")
                    time_iso = "PT0H0M"
            else:
                time_iso = "PT0H0M"  # Если время не указано, возвращаем нулевой интервал

            # Получаем дату
            timing_date = timing.get("date")

            # Собираем словарь тайминга
            timing_dict = {
                'order_serial': order_serial,
                'task_id': task_id,  # Только ID задачи
                'executor': executor_name,  # ФИО исполнителя строкой
                'time': time_iso,  # Время в формате ISO 8601
                'date': timing_date
            }
            timings_list.append(timing_dict)

            if debug:
                print(f"Добавлена запись о времени: Заказ {order_serial}, "
                      f"Задача ID: {task_id}, Исполнитель: {executor_name}, "
                      f"Время: {time_iso}, Дата: {timing_date}")

    if debug:
        print(f"Получено {len(timings_list)} записей о потраченном времени")

    return timings_list


def create_equipments_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей оборудования из КИС2 через REST API.
    Args:
        debug: Флаг для вывода отладочной информации
    Returns:
        Список словарей оборудования со следующими ключами:
        - 'name': Название оборудования
        - 'model': Модель оборудования
        - 'vendore_code': Артикул/код поставщика
        - 'description': Описание оборудования
        - 'type': Тип оборудования (строка)
        - 'manufacturer': Производитель (строка)
        - 'price': Цена
        - 'currency': Валюта (строка)
        - 'relevance': Актуальность (True/False)
        - 'price_date': Дата обновления цены
    """
    # Получаем данные о типах оборудования
    equipment_types_data = get_data_from_kis2("EquipmentType", debug)
    if not equipment_types_data:
        if debug:
            print("Не удалось получить данные о типах оборудования")
        equipment_types_dict = {}
    else:
        # Создаем словарь id:name для типов оборудования
        equipment_types_dict = {item["id"]: item["name"] for item in equipment_types_data if
                                "id" in item and "name" in item}
        if debug:
            print(f"Получено {len(equipment_types_dict)} типов оборудования")

    # Формируем словарь производителей с использованием get_entity_dict
    manufacturers_dict = get_entity_dict(
        entity_name="Manufacturers",
        default_value="Неизвестный производитель",
        debug=debug
    )

    if debug:
        print(f"Получено {len(manufacturers_dict)} производителей")
        print('manufacturers_dict', manufacturers_dict)
    print('manufacturers_dict', manufacturers_dict)

    # Получаем данные о валютах
    currencies_dict = get_currencies_dict(debug)

    # Получаем данные об оборудовании
    equipments_data = get_data_from_kis2("Equipment", debug)
    if not equipments_data:
        if debug:
            print("Не удалось получить данные об оборудовании")
        return []

    # Создаем список словарей оборудования
    equipments_list = []
    for equipment in equipments_data:
        # Проверяем наличие необходимых ключей
        if "name" in equipment and "model" in equipment:
            # Получаем тип оборудования
            type_id = equipment.get("type_id")
            type_name = equipment_types_dict.get(type_id, "Неизвестный тип")

            # Получаем производителя
            manufacturer_name = manufacturers_dict.get(equipment.get("manufacturer_id"))

            # Получаем валюту
            currency_id = equipment.get("currency_id")
            currency_name = currencies_dict.get(currency_id, "Неизвестная валюта")

            # Преобразуем дату обновления цены
            price_date_str = equipment.get("price_date")
            price_date = price_date_str if price_date_str else None

            # Собираем словарь оборудования
            equipment_dict = {
                'name': equipment["name"],
                'model': equipment["model"],
                'vendor_code': equipment.get("vendore_code", ""),
                'description': equipment.get("description", ""),
                'type': type_name,
                'manufacturer': f"{manufacturer_name}",
                'price': equipment.get("price", 0),
                'currency': currency_name,
                'relevance': equipment.get("relevance", True),
                'price_date': price_date
            }
            equipments_list.append(equipment_dict)

            if debug:
                print(f"Добавлено оборудование: {equipment['name']} (Модель: {equipment['model']})")

    if debug:
        print(f"Получено {len(equipments_list)} единиц оборудования")

    return equipments_list


def create_boxes_list_dict_from_kis2(debug: bool = True) -> List[Dict[str, Any]]:
    """
    Создаёт список словарей корпусов шкафов (Box) из КИС2 через REST API.

    Args:
        debug: Флаг для вывода отладочной информации

    Returns:
        Список словарей корпусов шкафов со следующими ключами:
        - 'equipment_id': ID оборудования/корпуса
        - 'equipment_name': Название оборудования
        - 'equipment_model': Модель оборудования
        - 'material': Материал корпуса
        - 'height': Высота корпуса
        - 'width': Ширина корпуса
        - 'depth': Глубина корпуса
        - 'ip': Степень защиты корпуса
        - 'manufacturer': Производитель оборудования
        - 'price': Цена
        - 'currency': Валюта (строка)
    """
    # Получаем данные о материалах корпусов
    box_materials_data = get_data_from_kis2("BoxMaterial", debug)
    if not box_materials_data:
        if debug:
            print("Не удалось получить данные о материалах корпусов")
        box_materials_dict = {}
    else:
        # Создаем словарь id:name для материалов корпусов
        box_materials_dict = {item["id"]: item["name"]
                              for item in box_materials_data
                              if "id" in item and "name" in item}
        if debug:
            print(f"Получено {len(box_materials_dict)} материалов корпусов")

    # Получаем данные о степенях защиты корпусов
    box_ip_data = get_data_from_kis2("BoxIp", debug)
    if not box_ip_data:
        if debug:
            print("Не удалось получить данные о степенях защиты корпусов")
        box_ip_dict = {}
    else:
        # Создаем словарь id:name для степеней защиты
        box_ip_dict = {item["id"]: item["name"]
                       for item in box_ip_data
                       if "id" in item and "name" in item}
        if debug:
            print(f"Получено {len(box_ip_dict)} степеней защиты корпусов")

    # Получаем данные об оборудовании
    equipment_data = get_data_from_kis2("Equipment", debug)
    if not equipment_data:
        if debug:
            print("Не удалось получить данные об оборудовании")
        equipment_dict = {}
    else:
        # Создаем словарь для быстрого доступа к данным об оборудовании
        equipment_dict = {item["id"]: item
                          for item in equipment_data
                          if "id" in item}
        if debug:
            print(f"Получено {len(equipment_dict)} единиц оборудования")

    # Получаем данные о производителях
    manufacturers_dict = get_entity_dict(
        entity_name="Manufacturers",
        default_value="Неизвестный производитель",
        debug=debug
    )

    # Получаем данные о валютах
    currencies_dict = get_currencies_dict(debug)

    # Получаем данные о корпусах шкафов
    boxes_data = get_data_from_kis2("Box", debug)
    if not boxes_data:
        if debug:
            print("Не удалось получить данные о корпусах шкафов")
        return []

    # Создаем список словарей корпусов шкафов
    boxes_list = []
    for box in boxes_data:
        # Проверяем наличие необходимого ключа equipment_id
        if "equipment_id" in box:
            equipment_id = box["equipment_id"]

            # Получаем данные об оборудовании, связанном с этим корпусом
            equipment = equipment_dict.get(equipment_id, {})

            # Получаем материал корпуса
            material_id = box.get("material_id")
            material_name = box_materials_dict.get(material_id, "Неизвестный материал") if material_id else None

            # Получаем степень защиты корпуса
            ip_id = box.get("ip_id")
            ip_name = box_ip_dict.get(ip_id, "Неизвестная степень защиты") if ip_id else None

            # Получаем производителя оборудования
            manufacturer_id = equipment.get("manufacturer_id")
            manufacturer_name = manufacturers_dict.get(manufacturer_id,
                                                       "Неизвестный производитель") if manufacturer_id else None

            # Получаем валюту
            currency_id = equipment.get("currency_id")
            currency_name = currencies_dict.get(currency_id, "Неизвестная валюта") if currency_id else None

            # Собираем словарь корпуса шкафа
            box_dict = {
                'equipment_id': equipment_id,
                'equipment_name': equipment.get("name", "Неизвестное оборудование"),
                'equipment_model': equipment.get("model", ""),
                'vendor_code': equipment.get("vendore_code", ""),
                'description': equipment.get("description", ""),
                'material': material_name,
                'height': box.get("height"),
                'width': box.get("width"),
                'depth': box.get("depth"),
                'ip': ip_name,
                'manufacturer': manufacturer_name,
                'price': equipment.get("price", 0),
                'currency': currency_name,
                'price_date': equipment.get("price_date", ""),
            }

            boxes_list.append(box_dict)

            if debug:
                print(f"Добавлен корпус шкафа: {box_dict['equipment_name']} "
                      f"(Материал: {material_name}, "
                      f"Размеры: {box.get('height')}x{box.get('width')}x{box.get('depth')})")

    if debug:
        print(f"Всего получено {len(boxes_list)} корпусов шкафов")

    return boxes_list


if __name__ == "__main__":
    boxes_list_dict_from_kis2 = create_boxes_list_dict_from_kis2()
    for timing in boxes_list_dict_from_kis2:
        print(timing)
