from fastapi import APIRouter, FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from starlette.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/test")


# Пример приветственного сообщения
@router.get("/hello_world")
def hello_world():
    return {"message": "Hello World!!"}


# Пример данных пользователей
users = [
    {'id': 1, 'name': "Bob", 'age': 10},
    {'id': 2, 'name': "Oleg", 'age': 20},
    {'id': 3, 'name': "David", 'age': 30},
    {'id': 4, 'name': "Ivan", 'age': 40},
    {'id': 5, 'name': "Petr", 'age': 50},
]


@router.get("/user/{user_id}")
def get_user(user_id: int):
    user = next((user for user in users if user.get('id') == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=user)


# Пример данных заказов
orders = [
    {'id': 1, 'name': "order1", 'priority': 5},
    {'id': 2, 'name': "order2", 'priority': 4},
    {'id': 3, 'name': "order3", 'priority': 3},
    {'id': 4, 'name': "order4", 'priority': 2},
    {'id': 5, 'name': "order5", 'priority': 1},
    {'id': 6, 'name': "order6", 'priority': 1},
]


@router.get("/order")
def get_orders(offset: int = 0, limit: int = 10):  # Увеличен по умолчанию limit до 10
    return orders[offset:offset + limit]


@router.get("/hello")
def hello_name(name: str):
    user_name = name.strip().title()
    return {"message": f"Hello {user_name}!"}


@router.get("/load_test_html_page")
def root():
    return FileResponse("content/HTML_example.html")


@router.get("/load_test_file")
def root():
    return FileResponse("content/test_file.txt",
                        filename="test_file.txt",
                        media_type="application/octet-stream")


@router.post("/summa")
def summa(data=Body()):
    a = data["a"]
    b = data["b"]
    return {"message": f"сумма а + в = {a + b}"}


class Multiplication(BaseModel):
    m1: int
    m2: int


@router.post("/mult")
def hello(multipliers: Multiplication):
    return {"message": f"произведение = {multipliers.m1 * multipliers.m2}"}