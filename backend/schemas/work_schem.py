# schemas/work_schem.py
"""
Схемы для заказов
"""

from pydantic import BaseModel, field_validator, computed_field
from typing import Optional
from typing import List
from datetime import datetime
from pydantic import ConfigDict

# --- WorkSchema (убедитесь, что она есть и настроена) ---
class WorkSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    active: bool = True

    # Убедитесь, что конфигурация соответствует вашей версии Pydantic
    model_config = ConfigDict(from_attributes=True) # Для Pydantic v2+
    # class Config: # Для Pydantic v1
    #     from_attributes = True