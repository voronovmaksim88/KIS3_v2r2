from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from typing import Dict
from colorama import Fore
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
@router.post("/countries/sync", response_model=Dict[str, str])
def import_countries_sync():
    """
    Импортирует страны из КИС2 в КИС3 синхронно.
    Возвращает результат только после завершения импорта.
    """
    try:
        # Выполняем импорт напрямую
        import_countries_from_kis2()
        return {"status": "success", "message": "Импорт стран успешно выполнен"}
    except Exception as e:
        logger.error(f"Ошибка при импорте стран: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при импорте стран: {str(e)}")