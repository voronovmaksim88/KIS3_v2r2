from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import models
import schemas


# Создание
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# Получение по ID
async def get_user(db: AsyncSession, user_id: int):
    query = select(models.User).where(models.User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# Получение списка
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(models.User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Обновление
async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate):
    query = select(models.User).where(models.User.id == user_id)
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
    query = select(models.User).where(models.User.id == user_id)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user


# Получение по username
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(models.User).where(models.User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# Получение по email
async def get_user_by_email(db: AsyncSession, email: str):
    query = select(models.User).where(models.User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()