# schemas/state.py
from datetime import datetime
from datetime import UTC
from loguru import logger


class DatabaseState:
    def __init__(self):
        self.last_edit = datetime.now(UTC)
        logger.info(f"Database state initialized at {self.last_edit}")

    def update_last_edit(self):
        self.last_edit = datetime.now(UTC)
        logger.info(f"Database last edit time updated to {self.last_edit}")


# Создаем глобальный объект для хранения состояния БД
db_state = DatabaseState()
