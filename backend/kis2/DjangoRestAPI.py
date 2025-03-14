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
            print(f"Читаемый ответ API: {pretty_json[:200]}...")

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


def create_def_list_dict_manufacturers(debug: bool = True) -> List[Dict[str, str]]:
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


if __name__ == "__main__":
    person_list_dict_from_kis2 = create_person_list_dict_from_kis2()
    for company in person_list_dict_from_kis2:
        print(company)
