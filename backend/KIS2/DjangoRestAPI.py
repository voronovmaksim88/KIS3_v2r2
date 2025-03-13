#  КИС2/DjangoRestAPI.py
import requests


def get_countries_set(debug=True):
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
            print(f"Первые 200 символов ответа API: {api_response.text[:200]}")

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

