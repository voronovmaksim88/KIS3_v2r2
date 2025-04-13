# schemas/timing_schem.py
"""
Схемы для таймингов
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from typing import List
from pydantic import ConfigDict
from schemas.work_schem import WorkSchema
from datetime import datetime, timedelta
import uuid
from schemas.task_schem import TaskSchema


# Схема для тайминга
class TimingSchema(BaseModel):
    id: int
    task_id: int
    executor_id: Optional[uuid.UUID] = None
    time: timedelta
    timing_date: Optional[datetime] = None

    class Config:
        from_attributes = True
