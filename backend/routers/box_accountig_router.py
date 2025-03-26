# router/box_accounting_router
"""
Все роутеры для учёта шкафов
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query

from auth.jwt_auth import get_current_auth_user
from database import get_async_db
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func
from models import BoxAccounting as BoxAccountingModel
from models import User as UserModel
from loguru import logger

from schemas import PaginatedBoxAccounting, BoxAccountingResponse

router = APIRouter(
    prefix="/box-accounting",
    tags=["box-accounting"],
)


@router.get("/read/", response_model=PaginatedBoxAccounting)
async def read_box_accounting(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user),
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
):
    """
    Получение списка учтенных шкафов.
    Возвращает все записи учета шкафов.
    Использует аутентификацию через куки.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to box accounting")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} fetching box accounting records")

        # Рассчитываем параметры пагинации
        # offset определяет, сколько записей нужно пропустить перед началом выборки.
        # Например, если page = 2 и size = 20, то offset = (2 - 1) * 20 = 20.
        # Это означает, что первые 20 записей будут пропущены, и выборка начнется с 21-й записи.
        offset = (page - 1) * size

        # Получаем общее количество записей в таблице BoxAccountingModel
        # func.count() используется для подсчета количества строк в таблице.
        count_stmt = select(func.count()).select_from(BoxAccountingModel)
        total_count = await db.execute(count_stmt)
        total = total_count.scalar()

        # Вычисляем общее количество страниц
        # Формула: (total + size - 1) // size
        # Пример: если total = 55 и size = 20, то total_pages = (55 + 20 - 1) // 20 = 74 // 20 = 3.
        # Если total = 0, то total_pages устанавливается в 1, чтобы избежать деления на ноль или отрицательных значений.
        total_pages = (total + size - 1) // size if total > 0 else 1

        # Получаем записи учета шкафов со связанными данными
        # joinedload используется для загрузки связанных данных (например, scheme_developer, assembler и т.д.)
        # Это позволяет избежать проблемы N+1 запросов к базе данных.
        stmt = select(BoxAccountingModel).options(
            joinedload(BoxAccountingModel.scheme_developer),
            joinedload(BoxAccountingModel.assembler),
            joinedload(BoxAccountingModel.programmer),
            joinedload(BoxAccountingModel.tester),
            joinedload(BoxAccountingModel.order)
        ).offset(offset).limit(size)  # Применяем пагинацию: пропускаем offset записей и выбираем size записей.

        result = await db.execute(stmt)
        boxes = result.scalars().unique().all()

        logger.info(
            f"Successfully retrieved {len(boxes)} box accounting records for user {current_user.username}"
        )

        # Преобразование ORM-объектов в Pydantic-схему
        box_responses = [BoxAccountingResponse.model_validate(box) for box in boxes]

        # Формируем ответ с пагинацией
        response = PaginatedBoxAccounting(
            items=box_responses,  # Передаем преобразованные объекты
            total=total,
            page=page,
            size=size,
            pages=total_pages
        )

        logger.info(
            f"Successfully retrieved {len(boxes)} box accounting records (page {page} of {total_pages})"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching box accounting records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch box accounting records",
        )
