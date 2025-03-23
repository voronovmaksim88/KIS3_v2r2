# routers/import_router.py
"""
Тут функции - роутеры для импорта данных
"""
from fastapi import APIRouter, HTTPException
from typing import Callable
import logging

# Импортируем функцию для импорта стран
from utils.import_data import *

# Создаем логгер
logger = logging.getLogger(__name__)

# Создаем роутер
router = APIRouter(
    prefix="/import",
    tags=["import"],
    responses={404: {"description": "Not found"}},
)


"""
Универсальный роутер для импорта данных
"""

# **Словарь с СИНХРОННЫМИ функциями импорта**
IMPORT_FUNCTIONS: Dict[str, Callable[[], Dict[str, Any]]] = {
    "countries": import_countries_from_kis2,
    "cities": import_cities_from_kis2,
    "currencies": import_currency_from_kis2,
    "manufacturers": import_manufacturers_from_kis2,
    "equipment_types": import_equipment_types_from_kis2,
    "counterparty_forms": import_counterparty_forms_from_kis2,
    "companies": import_companies_from_kis2,
    "people": import_people_from_kis2,
    "works": import_works_from_kis2,
    "order_statuses": ensure_order_statuses_exist,
    "orders": import_orders_from_kis2,
    "order_comments": import_order_comments_from_kis2,
    "boxes": import_boxes_from_kis2,
    "box_accounting": import_box_accounting_from_kis2,
    "tasks": import_tasks_from_kis2,

}


@router.post("/{entity}", response_model=Dict[str, Any])
def import_data(entity: str):
    """
    Универсальный асинхронный эндпоинт для импорта данных.

    :param entity: Тип данных для импорта (например, "countries" или "manufacturers")
    :return: JSONResponse с результатом импорта
    """

    if entity not in IMPORT_FUNCTIONS:
        raise HTTPException(status_code=400, detail=f"Неизвестная сущность для импорта: {entity}")

    try:
        # Вызываем нужную функцию импорта по имени
        import_function = IMPORT_FUNCTIONS[entity]
        result = import_function()
        return result

    except Exception as e:
        logger.error(f"Ошибка при импорте данных для '{entity}': {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при импорте {entity}: {str(e)}")
