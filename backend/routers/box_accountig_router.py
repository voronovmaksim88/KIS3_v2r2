# router/box_accounting_router
"""
Все роутеры для учёта шкафов
"""
import uuid
import models

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

from schemas import PaginatedBoxAccounting, BoxAccountingResponse, BoxAccountingCreate

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
        ).order_by(BoxAccountingModel.serial_num.desc()).offset(offset).limit(size)  # Добавлена сортировка
        # Применяем пагинацию: пропускаем offset записей и выбираем size записей.

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


async def _check_person_exists(db: AsyncSession, person_id: uuid.UUID) -> bool:
    """
    Вспомогательная функция для проверки существования человека по ID.
    """
    # Преобразуем person_id в строку или число, если модель ожидает такой тип
    result = await db.execute(
        select(models.Person).filter(models.Person.uuid == person_id)
    )
    return result.scalar_one_or_none() is not None


@router.post("/create/", response_model=BoxAccountingResponse, status_code=status.HTTP_201_CREATED)
async def create_box_accounting(
        box_data: BoxAccountingCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_auth_user),
):
    """
    Создание новой записи о серийном номере шкафа.
    Принимает данные о шкафе и сохраняет их в базе данных.
    Требует аутентификации пользователя.
    """
    try:
        # Проверяем, что пользователь авторизован
        if not current_user:
            logger.warning("Unauthorized access attempt to create box accounting record")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(f"User {current_user.username} creating new box accounting record")

        # Проверяем существование заказа
        order_check = select(func.count()).select_from(models.Order).where(models.Order.serial == box_data.order_id)
        order_exists = await db.execute(order_check)
        if order_exists.scalar() == 0:
            logger.warning(f"Order with ID {box_data.order_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {box_data.order_id} not found"
            )

        # Проверяем существование разработчика схемы
        if not await _check_person_exists(db, box_data.scheme_developer_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme developer with ID {box_data.scheme_developer_id} not found"
            )

        # Проверяем существование сборщика
        if not await _check_person_exists(db, box_data.assembler_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assembler with ID {box_data.assembler_id} not found"
            )

        # Проверяем существование программиста (если указан)
        if box_data.programmer_id and not await _check_person_exists(db, box_data.programmer_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programmer with ID {box_data.programmer_id} not found"
            )

        # Проверяем существование тестировщика
        if not await _check_person_exists(db, box_data.tester_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tester with ID {box_data.tester_id} not found"
            )

        # Получаем максимальный существующий serial_num
        max_serial_query = select(func.max(BoxAccountingModel.serial_num))
        result = await db.execute(max_serial_query)
        max_serial = result.scalar()

        # Генерируем новый serial_num (max + 1 или 1, если записей ещё нет)
        new_serial_num = 1 if max_serial is None else max_serial + 1

        logger.info(f"Automatically generating new serial_num: {new_serial_num}")

        # Создаем новую запись о шкафе с автоматически сгенерированным serial_num
        new_box = BoxAccountingModel(
            serial_num=new_serial_num,
            name=box_data.name,
            order_id=box_data.order_id,
            scheme_developer_id=box_data.scheme_developer_id,
            assembler_id=box_data.assembler_id,
            programmer_id=box_data.programmer_id,
            tester_id=box_data.tester_id
        )

        # Добавляем запись в базу данных
        db.add(new_box)
        await db.commit()
        await db.refresh(new_box)

        # Загружаем связанные данные для ответа
        await db.refresh(new_box, ["scheme_developer", "assembler", "programmer", "tester", "order"])

        logger.info(f"Successfully created box accounting record with serial number {new_box.serial_num}")

        # Преобразуем ORM-объект в Pydantic-модель для ответа
        return BoxAccountingResponse.model_validate(new_box)

    except HTTPException:
        # Пробрасываем HTTP-исключения дальше
        raise
    except Exception as e:
        # Логируем необработанные исключения и отправляем обобщенный ответ
        logger.error(f"Error creating box accounting record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create box accounting record: {str(e)}",
        )
