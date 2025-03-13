"""
Тут будем доставать данные из бд Sqlite3, которая в КИС2 использована, подключаться к её серверу я пока не стал,
тупо скопировал файл БД в папку
когда все эти функции будут переписаны с прямого подключения на API можно буде это файл переместить в папку old
"""
# Импорт необходимых библиотек
# from tabulate import tabulate
# from colorama import Fore
from colorama import init
import sqlite3
from typing import Set, Dict
from config import DB_PATH

# Инициализация colorama
init(autoreset=True)

# Путь к файлу базы данных
db_path = DB_PATH
print("путь к базе: " + db_path)
# Инициализируем colorama
init(autoreset=True)


def execute_query(query: str):
    """
    Выполняет SQL-запрос к базе данных SQLite.

    Args:
        query: SQL-запрос в виде строки.

    Returns:
        Список кортежей, представляющих строки результата запроса.
        В случае ошибки возвращается пустой список.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(query)
            return cur.fetchall()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return []


def get_set_countries() -> Set[str]:
    """
    :return: множество названий стран
    Например:{'Литва', 'Франция', 'Дания', 'США', 'Россия'}
    """
    results = execute_query("SELECT name FROM main_countries")
    # Создаём множество названий стран при помощи List comprehension
    countries_set = {country[0] for country in results}
    print(f"{len(countries_set)} countries in database sqlite3")
    return countries_set


def get_dict_countries() -> Dict[int, str]:
    """
    :return: словарь стран, ключ - id, значение - название страны.
    Например: {1: 'Россия', 2: 'Германия', 3: 'Дания', 4: 'Китай'}
    """
    results = execute_query("SELECT id, name FROM main_countries")
    countries_dict = {country_id: name for country_id, name in results}
    print(f"{len(countries_dict)} countries in database sqlite3")
    return countries_dict


def get_list_dict_manufacturers():
    """
    :return: список словарей производителей.
    Каждый словарь содержит ключ 'name'-название производителя, ключ 'country' - название страны
    Например - [{'name':'Zentec', country:'Россия'}, {'name':'Segnetics', country:'Россия'}].
    """
    # формируем множество названий стран, чтоб потом подставить их в список
    all_countries_dict = get_dict_countries()
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM main_manufacturers")
            all_manufacturers = cur.fetchall()
            all_manufacturers_list = []
            for manufacturer in all_manufacturers:
                # manufacturer[0] - это id записи о производителе
                # manufacturer[1] - это название производителя
                # manufacturer[2] - это id страны производителя
                print(manufacturer)
                all_manufacturers_list.append(
                    {'name': manufacturer[1], 'country': all_countries_dict.get(manufacturer[2])})
            return all_manufacturers_list
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return []  # empty list


def get_set_equipment_types():
    """
    :return: множество названий типов оборудования
    Например:{'inductance', 'bushing', 'sensors', 'diode', 'connector'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM main_equipmenttype")
            equipment_type_set = {equipment_type[0] for equipment_type in cur.fetchall()}
            print(f"{len(equipment_type_set)} equipment types in database sqlite3")
            return equipment_type_set
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return set()


def get_set_cities():
    """
    :return: множество названий городов
    Например:{'Москва', 'Санкт-Петербург', 'Казань', 'Новосибирск'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM main_city")
            cities_set = {city[0] for city in cur.fetchall()}
            print(f"{len(cities_set)} cities in database sqlite3")
            return cities_set
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return set()


def get_set_companies_form():
    """
    :return: множество названий форм собственности
    Например:{'ООО', 'ЗАО', 'ПАО', 'АО'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM main_companiesform")
            companies_form_set = {company_form[0] for company_form in cur.fetchall()}
            print(f"{len(companies_form_set)} companies form in database sqlite3")
            return companies_form_set
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return set()  # пустое множество


def get_dict_companies_form():
    """
    :return: словарь форм компаний (в КИС3 это будут контрагенты).
    Например:{'1': 'ООО', '2': 'ЗАО', '3': 'ПАО', '4': 'АО'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM main_companiesform")
            return {companiesform_id: name for companiesform_id, name in cur.fetchall()}
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return {}  # пустой словарь


def get_dict_cities():
    """
    :return: словарь городов.
    Ключ - id города, значение - название города.
    Например - {1: 'Новосибирск', 2: 'Москва', 3: 'Санкт-Петербург'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM main_city")
            return {city_id: name for city_id, name in cur.fetchall()}
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return {}  # пустой словарь


def get_list_dict_companies():
    """
    :return: список словарей компаний(в КИС3 это будут контрагенты).
    Каждый словарь содержит ключ 'name'-название компании, 'form' - форма компании, ключ 'city' - город,
    'note' - примечание.
    Например - [{'name':'СИБПЛК', 'form': 'ООО', city:'Новосибирск', note:'то мы'},
    {'name':'Вентавтоматика','form': 'ООО', city:'Москва', note:'отличные ребята'}].
    """
    # формируем необходимые словари
    dict_companies_form = get_dict_companies_form()
    dict_cities = get_dict_cities()
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM main_company")
            all_company = cur.fetchall()
            all_companies_list_dict = []
            for company in all_company:
                # company[0] - это id записи о компании
                # company[1] - это название компании
                # company[2] - это примечание
                # company[3] - это id формы компании
                # company[4] - это id города
                all_companies_list_dict.append(
                    {'name': company[1],
                     'note': company[2],
                     'form': dict_companies_form[company[3]],
                     'city': dict_cities[company[4]]
                     })
            return all_companies_list_dict
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return []  # empty list


def get_dict_companies():
    """
    :return: словарь компаний(в КИС3 это будут контрагенты).
    Ключ - id компании, значение - название компании.
    Например - {1: 'СИБПЛК', 2: 'Вентавтоматика'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM main_company")
            return {company_id: name for company_id, name in cur.fetchall()}
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return {}  # пустой словарь


def get_set_person():
    """
    :return: множество людей
    Например - {'Воронов Максим Владимирович','Иванов Иван Иванович', 'Петров Пётр Петрович'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT surname,name,patronymic FROM main_person")
            person_set = {person[0] + person[1] + person[2] for person in cur.fetchall()}
            print(f"{len(person_set)} persons in database sqlite3")
            return person_set
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return set()


def get_list_dict_person():
    """
    :return: список словарей людей.
    Каждый словарь содержит ключ 'name' - имя, 'patronymic' - отчество, 'surname' - фамилия, 'note' - примечание.
    Например:
     [
         {
            'name':'Максим',
            'patronymic':'Владимирович',
            'surname':'Воронов',
            'phone':'+7-913-899-5941',
            'email':'v@mail.ru',
            'company':'СИБПЛК',
        },
    ]
    """
    # формируем необходимые словари
    dict_companies = get_dict_companies()  # словарь компаний
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM main_person")
            all_person = cur.fetchall()
            all_person_list_dict = []
            for person in all_person:
                # person[0] - id записи о человеке
                # person[1] - имя
                # person[2] - отчество
                # person[3] - фамилия
                # person[4] - телефон
                # person[5] - email
                # person[6] - company_id
                all_person_list_dict.append({
                    'name': person[1],
                    'patronymic': person[2],
                    'surname': person[3],
                    'phone': person[4],
                    'email': person[5],
                    'company': dict_companies[person[6]]
                })
            return all_person_list_dict  # список словарей людей
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return []  # empty list


def get_dict_person():
    """
    :return: словарь людей, ключ - id человека, значение - фамилия, имя, отчество,
    Например:
    {1:'Воронов Максим Владимирович',
    2:'Иванов Иван Иванович',
    3:'Петров Пётр Петрович'}
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, surname, name, patronymic FROM main_person")
            person_dic = {person[0]: person[1] + person[2] + person[3] for person in cur.fetchall()}
            return person_dic
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return set()


def get_set_work():
    """
    :return: множество названий работ выполняемых по заказам
    Например - {'Продажа товаров','Разработка ПО для ПЛК', 'Сборка ША'}
    """
    results = execute_query("SELECT name FROM main_work")
    work_set = {work[0] for work in results}
    print(f"{len(work_set)} works in database sqlite3")
    return work_set


def get_dict_works():
    """
    :return: словарь работ.
    Словарь содержит ключ - id, значение - name
    Например - {'1':'Продажа товаров'},
    """
    results = execute_query("SELECT id, name FROM main_work")
    dict_works = {}
    for work in results:
        # work[0] - id
        # work[1] - name
        dict_works[work[0]] = work[1]
    return dict_works  # словарь работ


def get_list_dict_work():
    """
    :return: список словарей работ.
    Каждый словарь содержит ключ 'name' - название, 'description' - описание
    Например - [{'name':'Продажа товаров', 'description':'Продаём товары',
    'name':'Сборка ША', 'description':'собираем шкаф автоматики'},
    """
    results = execute_query("SELECT name, description FROM main_work")
    all_work_list_dict = []
    for work in results:
        # work[0] - название работы
        # work[1] - описание
        all_work_list_dict.append({
            'name': work[0],
            'description': work[1],
        })
    return all_work_list_dict  # список словарей людей


def get_set_orders():
    """
    :return: множество номеров заказов
    Например - {'001-01-2021', '002-01-2021'}
    """
    results = execute_query("SELECT serial FROM main_order")
    order_set = {order[0] for order in results}
    print(f"{len(order_set)} orders in database sqlite3")
    return order_set


def get_order_status(status_id):
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


def get_list_works(order_id: str):
    """
    :param order_id: Получает номер заказа
    :return: Список работ выполняемых по заказу, в виде строк
    Например - ['Продажа товаров', 'Сборка ША']
    """
    dict_works = get_dict_works()
    query = f"SELECT work_id FROM main_order_works WHERE order_id = '{order_id}'"
    results = execute_query(query)
    works_list = []
    for work in results:
        works_list.append(dict_works[work[0]])
    return works_list


def get_list_dict_orders():
    """
    :return: список словарей заказов.
    Каждый словарь содержит ключ:
        'serial' - номер,
        'name' - имя,
        'customer' - имя заказчика
        'priority' - приоритет
        'status' - статус
            #     0 = "Не определён"
            #     1 = "На согласовании"
            #     2 = "В работе"
            #     3 = "Просрочено"
            #     4 = "Выполнено в срок"
            #     5 = "Выполнено НЕ в срок"
            #     6 = "Не согласовано"
            #     7 = "На паузе"
        'start_moment' - Дата и время создания
        'deadline_moment' - Дата и время дедлайна
        'end_moment' - Дата и время окончания
        'works' - список работ
        'materials_cost' - Стоимость материалов плановая
        'materials_paid' - Материалы оплачены
        'products_cost' - Стоимость материалов плановая
        'products_paid' - Товары оплачены
        'work_cost' - Стоимость работ плановая
        'work_paid' - Работы оплачены
        'debt' - Задолженность нам
        'debt_paid' - Задолженность оплачена

    Например:
    [
        {'serial': '029-05-2024',
         'name': 'наладка космодрома',
         'customer': 'Банк всемдаёмденег',
         'priority': 0,
         'status': 'На согласовании',
         'start_moment': '2024-05-18 16:49:55',
         'deadline_moment': '2024-06-17 21:00:00',
         'end_moment': None,
         'works': ['Наладка почему-то', 'Дезинфекция'],
         'materials_cost': 10,
         'materialsPaid': 0,
         'products_cost': 20,
         'productsPaid': 1,
         'work_cost': 0,
         'workPaid': 0,
         'debt': 123,
         'debtPaid': 1
        },
    ]
    """
    results = execute_query(
        "SELECT serial, name, customer_id, priority, status, start_moment, dedline_moment, end_moment, materialsCost,"
        " materialsPaid, productsCost, productsPaid, workCost, workPaid, debt, debtPaid FROM main_order")
    all_order_list_dict = []
    dict_companies = get_dict_companies()
    for order in results:
        # order[0] - serial
        # order[1] - name
        # order[2] - customer_id
        # order[3] - priority
        # order[4] - status
        # order[5] - start_moment
        # order[6] - dedline_moment
        # order[7] - end_moment
        # order[8] - materialsCost
        # order[9] - materialsPaid
        # order[10] - productsCost
        # order[11] - productsPaid
        # order[12] - workCost
        # order[13] - workPaid
        # order[14] - debt
        # order[15] - debtPaid
        all_order_list_dict.append({
            'serial': order[0],
            'name': order[1],
            'customer': dict_companies[order[2]],
            'priority': order[3],
            'status': get_order_status(order[4]),
            'start_moment': order[5],
            'deadline_moment': order[6],
            'end_moment': order[7],
            'works': get_list_works(order[0]),
            'materials_cost': order[8],
            'materialsPaid': order[9],
            'products_cost': order[10],
            'productsPaid': order[11],
            'work_cost': order[12],
            'workPaid': order[13],
            'debt': order[14],
            'debtPaid': order[15],
        })
    return all_order_list_dict  # список словарей заказов 'work_cost': get_list_works(order[0]),


def get_list_dict_box_accounting():
    """
    :return: список словарей записей учёта шкафов.
    Каждый словарь содержит ключ:
        'serial_num' - серийный номер,
        'name' - имя,
        'order_id' - заказ,
        'scheme_developer_id' - разработчик схемы,
        'assembler_id' - сборщик,
        'programmer_id' - программист,
        'tester_id' - тестировщик,
    """
    dict_person = get_dict_person()
    results = execute_query(
        "SELECT serial_num, name, order_id, scheme_developer_id, assembler_id, programmer_id, tester_id"
        "  FROM main_box_accounting")
    all_box_accounting_list_dict = []
    for res in results:
        # res[0] - serial_num
        # res[1] - name
        # res[2] - order_id
        # res[3] - scheme_developer_id
        # res[4] - assembler_id
        # res[5] - programmer_id
        # res[6] - tester_id
        if res[5]:
            programmer_id = dict_person[res[5]]
        else:
            programmer_id = 0
        all_box_accounting_list_dict.append({
            'serial_num': res[0],
            'name': res[1],
            'order_id': res[2],
            'scheme_developer': dict_person[res[3]],
            'assembler': dict_person[res[4]],
            'programmer': programmer_id,
            'tester': dict_person[res[6]],
        })

    return all_box_accounting_list_dict


def get_list_dict_order_comment():
    """
    :return: список словарей комментариев к заказам.
    Каждый словарь содержит ключ:
        'order_id' - заказ,
        'text' - комментарий,
        'moment_of_creation' - дата создания,
        'person_id' - автор комментария,
    """
    dict_person = get_dict_person()
    results = execute_query(
        "SELECT order_id, text, moment_of_creation, person_id FROM main_ordercoment")
    all_order_comment_list_dict = []
    for res in results:
        # res[0] - order_id
        # res[1] - text
        # res[2] - moment_of_creation
        # res[3] - person_id
        all_order_comment_list_dict.append({
            'order_id': res[0],
            'text': res[1],
            'moment_of_creation': res[2],
            'person': dict_person[res[3]],
        })

    return all_order_comment_list_dict


def print_list(list_for_print: list):
    for element in list_for_print:
        print(element)


# print(get_set_countries())
# print(get_dict_countries())
# print(get_set_work())
# print(get_list_dict_work())
# print(get_set_orders())
# print_list(get_list_dict_orders())
# print(get_dict_works())

# Получаем список заказов
# orders = get_list_dict_orders()

# Определяем заголовки таблицы как словарь
headers = {
    'serial': 'Серийный номер',
    'name': 'Название',
    'customer': 'Заказчик',
    'priority': 'Приоритет',
    'status': 'Статус'
}

# Выводим таблицу заказов с заголовками
# print(Fore.LIGHTBLUE_EX + tabulate(orders, headers=headers, tablefmt='grid'))

# print(get_list_works("029-05-2024"))
# print_list(get_list_dict_box_accounting())
# print(get_dict_person())
# print_list(get_list_dict_order_comment())
