# routers/import_router.py
"""
Тут функции - роутеры для импорта данных
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Callable
import logging

# Импортируем функцию для импорта стран
from utils.import_data import import_countries_from_kis2
from utils.import_data import import_manufacturers_from_kis2
from utils.import_data import import_equipment_types_from_kis2

# Создаем логгер
logger = logging.getLogger(__name__)

# Создаем роутер
router = APIRouter(
    prefix="/import",
    tags=["import"],
    responses={404: {"description": "Not found"}},
)

# синхронный эндпоинт, если вы предпочитаете получать результат сразу
# @router.post("/countries", response_model=Dict[str, Any])
# def import_countries_sync():
#     """
#     Импортирует страны из КИС2 в КИС3 синхронно.
#     Возвращает результат только после завершения импорта.
#     returns:
#     JSONResponse
#     {
#       "status": "success",
#       "added": 0,
#       "updated": 0,
#       "unchanged": 21
#     }
#     """
#     try:
#         # Выполняем импорт напрямую и получаем полный словарь результата
#         result = import_countries_from_kis2()
#         return result
#     except Exception as e:
#         logger.error(f"Ошибка при импорте стран: {e}")
#         raise HTTPException(status_code=500, detail=f"Ошибка при импорте стран: {str(e)}")
#
#
# @router.post("/manufacturers", response_model=Dict[str, Any])
# def import_manufacturers_sync():
#     """
#     Импортирует производителей из КИС2 в КИС3 синхронно.
#     Возвращает результат только после завершения импорта.
#     returns:
#     JSONResponse
#     {
#       "status": "success",
#       "added": 0,
#       "updated": 0,
#       "unchanged": 21
#     }
#     """
#     try:
#         # Выполняем импорт напрямую и получаем полный словарь результата
#         result = import_manufacturers_from_kis2()
#         return result
#     except Exception as e:
#         logger.error(f"Ошибка при импорте производителей: {e}")
#         raise HTTPException(status_code=500, detail=f"Ошибка при импорте производителей: {str(e)}")


"""
Универсальный роутер для импорта данных
"""

# **Словарь с СИНХРОННЫМИ функциями импорта**
IMPORT_FUNCTIONS: Dict[str, Callable[[], Dict[str, Any]]] = {
    "countries": import_countries_from_kis2,
    "manufacturers": import_manufacturers_from_kis2,
    "equipment_types": import_equipment_types_from_kis2,
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
