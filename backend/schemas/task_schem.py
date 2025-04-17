# schemas/task_schem.py
"""
Схемы для заказов
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, timedelta
import uuid


# Схема для задачи
class TaskSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status_id: Optional[int] = None
    payment_status_id: Optional[int] = None
    executor: str = None
    planned_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    creation_moment: Optional[datetime] = None
    start_moment: Optional[datetime] = None
    deadline_moment: Optional[datetime] = None
    end_moment: Optional[datetime] = None
    price: Optional[int] = None
    parent_task_id : Optional[int] = None
    root_task_id : Optional[int] = None

    class Config:
        from_attributes = True
