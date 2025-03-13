#  КИС2/DjangoRestAPI.py
import requests


def create_countries_set_from_kis2(debug=True):
    base_url = "https://kis2test.sibplc.ru"
    login_url = f"{base_url}/accounts/login/"
    api_url = f"{base_url}/api/Countries/"

    username = "admin"
    password = "djangoadmin"

    # Создаем сессию для сохранения куки
    session = requests.Session()
    api_response = None  # Инициализируем переменную

    try:
        # Получаем страницу логина для получения CSRF токена
        login_page = session.get(login_url)

        if debug:
            print(f"Получение страницы логина: {login_page.status_code}")

        # Находим CSRF токен в HTML-странице
        if 'csrfmiddlewaretoken' in login_page.text:
            import re
            csrf_token = re.search('name="csrfmiddlewaretoken" value="(.+?)"', login_page.text).group(1)
            if debug:
                print(f"CSRF Token: {csrf_token}")
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
            return set()

        # Получаем данные API используя ту же сессию
        api_response = session.get(api_url)

        if debug:
            print(f"Статус API запроса: {api_response.status_code}")
            print(f"Content-Type: {api_response.headers.get('Content-Type', '')}")

            # Декодируем Unicode-escape последовательности для отображения
            import json
            pretty_json = json.dumps(api_response.json(), ensure_ascii=False, indent=2)
            print(f"Читаемый ответ API: {pretty_json[:200]}...")

            # Исходный вывод для сравнения
            print(f"Исходный ответ API: {api_response.text[:200]}...")

        # Проверяем успешность запроса
        api_response.raise_for_status()

        # Проверяем, что получили JSON, а не HTML
        if 'text/html' in api_response.headers.get('Content-Type', ''):
            print("Получен HTML вместо JSON, возможно, авторизация не сработала")
            if debug:
                print(f"Полный ответ: {api_response.text}")
            return set()

        # Парсим JSON
        countries_data = api_response.json()

        # Проверяем, что данные имеют ожидаемую структуру
        if not isinstance(countries_data, list):
            print(f"Ожидался список, но получен: {type(countries_data)}")
            return set()

        # Создаем множество из названий стран (используем другое имя переменной)
        countries_set = {item["name"] for item in countries_data if "name" in item}

        return countries_set

    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP запроса: {e}")
        return set()
    except ValueError as e:
        print(f"Ошибка при разборе JSON: {e}")
        if debug and api_response is not None:
            print(f"Текст ответа: {api_response.text}")
        return set()
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return set()


def create_def_list_dict_manufacturers(debug=True):
    """
    Получает список производителей из КИС2 через REST API.

    :param debug: Флаг для вывода отладочной информации
    :return: список словарей производителей.
    Каждый словарь содержит ключ 'name'-название производителя, ключ 'country' - название страны
    Например - [{'name':'Zentec', country:'Россия'}, {'name':'Segnetics', country:'Россия'}].
    """
    base_url = "https://kis2test.sibplc.ru"
    login_url = f"{base_url}/accounts/login/"
    manufacturers_api_url = f"{base_url}/api/Manufacturers/"
    countries_api_url = f"{base_url}/api/Countries/"

    username = "admin"
    password = "djangoadmin"

    # Создаем сессию для сохранения куки
    session = requests.Session()
    manufacturers_response = None
    countries_response = None

    try:
        # Получаем страницу логина для получения CSRF токена
        login_page = session.get(login_url)

        if debug:
            print(f"Получение страницы логина: {login_page.status_code}")

        # Находим CSRF токен в HTML-странице
        if 'csrfmiddlewaretoken' in login_page.text:
            import re
            csrf_token = re.search('name="csrfmiddlewaretoken" value="(.+?)"', login_page.text).group(1)
            if debug:
                print(f"CSRF Token: {csrf_token}")
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
            return []

        # Получаем данные о странах
        countries_response = session.get(countries_api_url)

        if debug:
            print(f"Статус API запроса стран: {countries_response.status_code}")

        # Проверяем успешность запроса
        countries_response.raise_for_status()

        # Проверяем, что получили JSON, а не HTML
        if 'text/html' in countries_response.headers.get('Content-Type', ''):
            print("Получен HTML вместо JSON при запросе стран, возможно, авторизация не сработала")
            if debug:
                print(f"Полный ответ стран: {countries_response.text}")
            return []

        # Парсим JSON стран
        countries_data = countries_response.json()

        # Проверяем, что данные имеют ожидаемую структуру
        if not isinstance(countries_data, list):
            print(f"Ожидался список стран, но получен: {type(countries_data)}")
            return []

        # Создаем словарь id:name для стран
        countries_dict = {item["id"]: item["name"] for item in countries_data if "id" in item and "name" in item}

        if debug:
            print(f"Получено {len(countries_dict)} стран")

        # Получаем данные о производителях
        manufacturers_response = session.get(manufacturers_api_url)

        if debug:
            print(f"Статус API запроса производителей: {manufacturers_response.status_code}")

        # Проверяем успешность запроса
        manufacturers_response.raise_for_status()

        # Проверяем, что получили JSON, а не HTML
        if 'text/html' in manufacturers_response.headers.get('Content-Type', ''):
            print("Получен HTML вместо JSON при запросе производителей, возможно, авторизация не сработала")
            if debug:
                print(f"Полный ответ производителей: {manufacturers_response.text}")
            return []

        # Парсим JSON производителей
        manufacturers_data = manufacturers_response.json()

        # Проверяем, что данные имеют ожидаемую структуру
        if not isinstance(manufacturers_data, list):
            print(f"Ожидался список производителей, но получен: {type(manufacturers_data)}")
            return []

        # Создаем список словарей производителей
        manufacturers_list = []
        for manufacturer in manufacturers_data:
            # Проверяем наличие необходимых ключей
            if "name" in manufacturer and "country" in manufacturer:
                country_id = manufacturer["country"]
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

    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP запроса: {e}")
        return []
    except ValueError as e:
        print(f"Ошибка при разборе JSON: {e}")
        if debug:
            if manufacturers_response is not None:
                print(f"Текст ответа производителей: {manufacturers_response.text}")
            if countries_response is not None:
                print(f"Текст ответа стран: {countries_response.text}")
        return []
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return []
