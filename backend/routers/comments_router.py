# comments_router.py
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
# Убедитесь, что select импортирован правильно, если он используется где-то еще
# from sqlalchemy.future import select
from models import OrderComment, Person, Order # Импортируем Person и Order для проверки существования
from database import get_async_db
from pydantic import BaseModel, ConfigDict

router = APIRouter()

# --- Pydantic Schemas ---

# Схема для создания комментария (входные данные)
class CommentCreate(BaseModel):
    order_id: str
    text: str
    person_uuid: uuid.UUID # Используем UUID

# Схема для ответа (выходные данные)
class CommentResponse(BaseModel):
    id: int
    order_id: str
    moment_of_creation: Optional[datetime] # Момент создания может быть None, если default не сработал до commit
    text: str
    person_uuid: uuid.UUID # Используем UUID

    # Конфигурация для совместимости с ORM-моделями SQLAlchemy
    # Для Pydantic v2+
    model_config = ConfigDict(from_attributes=True)


# --- API Endpoint ---

@router.post(
    '/comments/create', # ИЗМЕНЕННЫЙ ПУТЬ
    response_model=CommentResponse, # Используем Pydantic-схему для ответа
    summary="Создать новый комментарий к заказу",
    tags=["comments"] # Добавляем тег для группировки в документации
)
async def create_comment(
    comment_data: CommentCreate, # Используем схему для валидации входных данных
    session: AsyncSession = Depends(get_async_db)
):
    """
    Создает новый комментарий для указанного заказа.

    - **order_id**: Серийный номер заказа (формат NNN-MM-YYYY).
    - **text**: Текст комментария.
    - **person_uuid**: UUID автора комментария.
    """
    # Опционально: Проверка существования пользователя (Person)
    # Это может потребовать дополнительного запроса к БД
    author = await session.get(Person, comment_data.person_uuid)
    if not author:
        raise HTTPException(status_code=404, detail=f"Person with UUID {comment_data.person_uuid} not found")

    # Опционально: Проверка существования заказа (Order)
    # Это также потребует доп. запроса
    # order = await session.get(Order, comment_data.order_id)
    # if not order:
    #     raise HTTPException(status_code=404, detail=f"Order with serial {comment_data.order_id} not found")


    # Создаем объект SQLAlchemy модели
    new_comment = OrderComment(
        order_id=comment_data.order_id,
        text=comment_data.text,
        person_uuid=comment_data.person_uuid
        # moment_of_creation установится по умолчанию в БД или SQLAlchemy
    )
    try:
        session.add(new_comment)
        await session.commit()
        await session.refresh(new_comment) # Обновляем объект, чтобы получить id и moment_of_creation
    except Exception as e:
        await session.rollback()
        # Логирование ошибки может быть полезно здесь
        print(f"Error creating comment: {e}") # Просто для примера
        raise HTTPException(status_code=500, detail="Could not save comment to the database")

    # FastAPI автоматически преобразует new_comment в CommentResponse благодаря orm_mode/from_attributes
    return new_comment


