# routers/import_router.py
"""
Тут функции - роутеры для импорта данных
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

# Импортируем функцию для импорта стран
from utils.import_data import import_countries_from_kis2

# Создаем логгер
logger = logging.getLogger(__name__)

# Создаем роутер
router = APIRouter(
    prefix="/import",
    tags=["import"],
    responses={404: {"description": "Not found"}},
)


# синхронный эндпоинт, если вы предпочитаете получать результат сразу
@router.post("/countries", response_model=Dict[str, Any])
def import_countries_sync():
    """
    Импортирует страны из КИС2 в КИС3 синхронно.
    Возвращает результат только после завершения импорта.
    returns:
    JSONResponse
    {
      "status": "success",
      "added": 0,
      "updated": 0,
      "unchanged": 21
    }
    """
    try:
        # Выполняем импорт напрямую и получаем полный словарь результата
        result = import_countries_from_kis2()
        return result
    except Exception as e:
        logger.error(f"Ошибка при импорте стран: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при импорте стран: {str(e)}")
