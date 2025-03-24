# auth/jwt_auth.py
from schemas.user import UserSchema
from auth import utils as auth_utils
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User as UserModel
from datetime import datetime, UTC
from loguru import logger
from core.config import settings

from fastapi import Body
from auth.utils import get_password_hash
from schemas.user import UserCreate, UserBase
from user_CRUD import get_user_by_email, get_user_by_username
from fastapi import Response, Cookie
from fastapi.security import APIKeyCookie
from typing import Optional

# Создаем схему для работы с cookie вместо OAuth2
cookie_scheme = APIKeyCookie(name="access_token")

# Обновляем конфигурацию для cookie
COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 24 * 60 * 365  # год в секундах


# Схема ответа с токеном
class TokenInfo(BaseModel):
    access_token: str  # JWT токен
    token_type: str  # Тип токена (Bearer)


# Создаем роутер с префиксом /jwt
router = APIRouter(prefix=f"{settings.api_v1_prefix}/jwt", tags=["JWT"])


# Настраиваем OAuth2 с указанием URL для получения токена
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/jwt/login/",  # Обновляем URL для получения токена
)


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """
    Проверяет учетные данные пользователя в базе данных.

    Args:
        username (str): Имя пользователя из формы
        password (str): Пароль пользователя из формы
        db (AsyncSession): Асинхронная сессия базы данных

    Returns:
        User: Объект пользователя если аутентификация успешна

    Raises:
        HTTPException:
            - 401 если имя пользователя или пароль неверны
            - 500 при ошибке работы с базой данных
    """
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    try:
        # Ищем пользователя в БД
        query = select(UserModel).filter(UserModel.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise unauthed_exc

        # Проверяем пароль
        if not auth_utils.check_password(
            password=password,
            hashed=user.hashed_password,  # Используем hashed_password из модели
        ):
            raise unauthed_exc

        # # Проверяем активность пользователя
        # if not user.active:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="user inactive",
        #     )

        # Обновляем время последнего входа
        user.last_login = datetime.now(UTC)
        await db.commit()

        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error during user validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        )


async def get_current_token_payload(
    access_token: Optional[str] = Cookie(None, alias=COOKIE_NAME),
) -> dict:
    """
    Получает и проверяет JWT токен из cookie
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = auth_utils.decode_jwt(token=access_token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """
    Получает текущего пользователя по данным из токена.

    Args:
        payload (dict): Данные из JWT токена
        db (AsyncSession): Асинхронная сессия базы данных

    Returns:
        UserModel: Объект пользователя из базы данных

    Raises:
        HTTPException:
            - 401 если пользователь не аутентифицирован
            - 401 если токен недействителен
            - 401 если пользователь не найден
            - 500 при ошибке работы с базой данных
    """
    try:
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        # Получаем ID пользователя из payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
            )

        # Преобразуем ID в целое число
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
            )

        # Получаем пользователя из базы данных
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"User with ID {user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Можно добавить дополнительные проверки
        # Например, проверку активности пользователя
        # if not user.is_active:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="User is inactive",
        #     )

        logger.debug(f"Successfully authenticated user: {user.username}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_auth_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        )


@router.post("/login/")
def auth_user_issue_jwt(
    response: Response,
    user: UserSchema = Depends(validate_auth_user),
):
    """
    Эндпоинт для логина пользователя.
    Создает JWT токен и устанавливает его в cookie
    """
    logger.info(f"Login attempt for user: {user.username}")

    try:
        jwt_payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
        }

        token = auth_utils.encode_jwt(payload=jwt_payload)

        # Устанавливаем cookie
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            max_age=COOKIE_MAX_AGE,
            httponly=True,  # Защита от XSS
            secure=False,  # для локальной разработки false, для production true
            samesite="lax",  # Защита от CSRF
            path="/",  # путь, для которого доступна куки
        )

        logger.success(f"Successfully generated JWT token for user {user.username}")

        return {"message": "Successfully logged in"}

    except Exception as e:
        logger.error(
            f"Failed to generate JWT token for user {user.username} | "
            f"Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating authentication token",
        )


@router.get("/users/me/")
async def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_auth_user),
):
    """
    Эндпоинт для получения информации о текущем пользователе.
    Требует валидный JWT токен
    """
    iat = payload.get("iat")  # время создания токена
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
        # "created_at": user.created_at,
        # "last_login": user.last_login,
        # "managed_projects": [p.id for p in user.managed_projects],
    }


@router.post("/register/", response_model=UserBase)
async def register_user(
    user_data: UserCreate = Body(...), db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.

    Args:
        user_data: Данные нового пользователя
        db: Асинхронная сессия базы данных

    Returns:
        User: Созданный пользователь

    Raises:
        HTTPException:
            - 400 если пользователь с таким email или username уже существует
            - 500 при ошибке работы с базой данных
    """
    try:
        # Проверяем, существует ли пользователь с таким email
        existing_email = await get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Проверяем, существует ли пользователь с таким username
        existing_username = await get_user_by_username(db, user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Хешируем пароль
        hashed_password = get_password_hash(user_data.password)

        # Создаем объект пользователя
        new_user = UserModel(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            created_at=datetime.now(UTC),
        )

        # Сохраняем в базу
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"Successfully created new user: {new_user.username}")

        # Возвращаем данные пользователя без пароля
        return UserBase(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            # created_at=new_user.created_at,
            # last_login=new_user.last_login,
            # managed_projects=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        )


@router.post("/logout/")
def logout(response: Response):
    """
    Эндпоинт для выхода пользователя.
    Удаляет cookie с токеном
    """
    response.delete_cookie(key=COOKIE_NAME, httponly=True, secure=True, samesite="lax")
    return {"message": "Successfully logged out"}
