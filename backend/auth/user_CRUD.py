# user_CRUD.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User as UserModel
import schemas
from sqlalchemy import func


# Создание
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# Получение по ID
async def get_user(db: AsyncSession, user_id: int):
    # Получаем пользователя из базы данных
    query = select(UserModel).where(UserModel.id == user_id)  # type: ignore
    result = await db.execute(query)
    return result.scalar_one_or_none()


# Получение списка
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(UserModel).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Обновление
async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate):
    # Получаем пользователя из базы данных
    query = select(UserModel).where(UserModel.id == user_id)  # type: ignore
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user:
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
    return db_user


# Удаление
async def delete_user(db: AsyncSession, user_id: int):
    # Получаем пользователя из базы данных
    query = select(UserModel).where(UserModel.id == user_id)  # type: ignore
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user


# Получение по username
async def get_user_by_username(db: AsyncSession, username: str):
    # Ищем пользователя в БД по имени
    query = select(UserModel).where(UserModel.username == username)  # type: ignore
    result = await db.execute(query)
    return result.scalar_one_or_none()


# Получение по email
async def get_user_by_email(db: AsyncSession, email: str):
    # Ищем пользователя в БД по email
    query = select(UserModel).where(func.lower(UserModel.email) == func.lower(email))  # type: ignore
    result = await db.execute(query)
    return result.scalar_one_or_none()
