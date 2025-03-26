# router/box_accountig_router
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from auth.jwt_auth import get_current_auth_user
from database import get_async_db
from schemas import BoxAccountingResponse
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models import BoxAccounting as BoxAccountingModel
from models import User as UserModel
from loguru import logger

router = APIRouter(prefix="/box-accounting")


@router.get("/read/", response_model=List[BoxAccountingResponse])
async def read_box_accounting(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user),
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

        # Получаем все записи учета шкафов со связанными данными
        stmt = select(BoxAccountingModel).options(
            joinedload(BoxAccountingModel.scheme_developer),
            joinedload(BoxAccountingModel.assembler),
            joinedload(BoxAccountingModel.programmer),
            joinedload(BoxAccountingModel.tester),
            joinedload(BoxAccountingModel.order)
        )
        result = await db.execute(stmt)
        boxes = result.scalars().unique().all()

        logger.info(
            f"Successfully retrieved {len(boxes)} box accounting records for user {current_user.username}"
        )
        return boxes

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching box accounting records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch box accounting records",
        )



#
#
#     # от claude
#     @router.get("/boxes/", response_model=PaginatedBoxAccounting)
# async def read_box_accounting(
#         page: int = Query(1, ge=1, description="Номер страницы"),
#         size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
#         db: AsyncSession = Depends(get_db),
#         current_user: UserModel = Depends(get_current_auth_user),
# ):
#     """
#     Получение списка учета шкафов с пагинацией.
#     Возвращает данные о шкафах для авторизованного пользователя.
#     Использует аутентификацию через куки.
#     """
#     try:
#         # Проверяем, что пользователь авторизован
#         if not current_user:
#             logger.warning("Unauthorized access attempt to box accounting")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Authentication required",
#             )
#
#         logger.debug(f"User {current_user.username} fetching box accounting data")
#
#         # Рассчитываем параметры пагинации
#         offset = (page - 1) * size
#
#         # Получаем общее количество записей
#         count_stmt = select(func.count()).select_from(BoxAccountingModel)
#         total_count = await db.execute(count_stmt)
#         total = total_count.scalar()
#
#         # Вычисляем общее количество страниц
#         total_pages = (total + size - 1) // size if total > 0 else 1
#
#         # Получаем данные с учетом пагинации
#         stmt = (
#             select(BoxAccountingModel)
#             .options(
#                 joinedload(BoxAccountingModel.scheme_developer),
#                 joinedload(BoxAccountingModel.assembler),
#                 joinedload(BoxAccountingModel.programmer),
#                 joinedload(BoxAccountingModel.tester)
#             )
#             .offset(offset)
#             .limit(size)
#         )
#
#         result = await db.execute(stmt)
#         boxes = result.scalars().all()
#
#         # Формируем ответ с пагинацией
#         response = PaginatedBoxAccounting(
#             items=boxes,
#             total=total,
#             page=page,
#             size=size,
#             pages=total_pages
#         )
#
#         logger.info(
#             f"Successfully retrieved {len(boxes)} box accounting records (page {page} of {total_pages})"
#         )
#         return response
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching box accounting data: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to fetch box accounting data",
#         )
