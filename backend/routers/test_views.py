from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/test")


# Пример приветственного сообщения
@router.get("/hello_world")
def hello_world():
    return {"message": "Hello World!!"}


@router.get("/hello")
def hello_name(name: str):
    user_name = name.strip().title()
    return {"message": f"Hello {user_name}!"}


# Пример данных пользователей
users = [
    {'id': 1, 'name': "Bob", 'age': 10},
    {'id': 2, 'name': "Oleg", 'age': 20},
    {'id': 3, 'name': "David", 'age': 30},
    {'id': 4, 'name': "Ivan", 'age': 40},
    {'id': 5, 'name': "Petr", 'age': 50},
]


@router.get("/get_user/{user_id}")
def get_user(user_id: int):
    user = next((user for user in users if user.get('id') == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=user)


# Pydantic модель для обновления пользователя
class UserNameUpdate(BaseModel):
    new_name: str


@router.post("/change_user_name/{user_id}")
def change_user_name(user_id: int, user_update: UserNameUpdate):
    # current_user = next((user for user in users if user.get("id") == user_id), None)
    current_user = None
    for user in users:
        if user.get("id") == user_id:
            current_user = user
            break
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    current_user['name'] = user_update.new_name  # Обновляем имя пользователя
    return {'status': 200, 'data': current_user}


@router.get("/load_test_html_page")
def root():
    return FileResponse("../content/HTML_example.html")


@router.get("/load_test_file")
def root():
    return FileResponse("../content/test_file.txt",
                        filename="test_file.txt",
                        media_type="application/octet-stream")


@router.post("/summa")
def summa(data=Body()):
    a = data["a"]
    b = data["b"]
    return {"message": f"а + в = {a + b}"}


class Multiplication(BaseModel):
    m1: int
    m2: int


@router.post("/mult")
def mult(multipliers: Multiplication):
    return {"message": f"а * в = {multipliers.m1 * multipliers.m2}"}


# Пример данных заказов
orders = [
    {'id': 1, 'name': "order1", 'priority': 10},
    {'id': 2, 'name': "order2", 'priority': 9},
    {'id': 3, 'name': "order3", 'priority': 8},
    {'id': 4, 'name': "order4", 'priority': 7},
    {'id': 5, 'name': "order5", 'priority': 6},
    {'id': 6, 'name': "order6", 'priority': 5},
    {'id': 7, 'name': "order7", 'priority': 4},
    {'id': 8, 'name': "order8", 'priority': 3},
    {'id': 9, 'name': "order9", 'priority': 2},
    {'id': 10, 'name': "order10", 'priority': 1},
]


@router.get("/order")
def get_orders(offset: int = 0, limit: int = 10):  # Увеличен по умолчанию limit до 10
    return orders[offset:offset + limit]


@router.get("/current_datetime")
def get_current_datetime():
    now = datetime.now()  # получение текущей даты и времени
    return {"current_datetime": now.isoformat()}  # возвращаем время в формате ISO 8601
