#  schemas / box_accounting_schem.py
from pydantic import BaseModel
from typing import Optional, List
import uuid


class PersonBase(BaseModel):
    uuid: uuid.UUID
    name: str
    surname: str

    class Config:
        orm_mode = True


class BoxAccountingBase(BaseModel):
    serial_num: int
    name: str
    order_id: str


class BoxAccountingCreate(BoxAccountingBase):
    scheme_developer_id: uuid.UUID
    assembler_id: uuid.UUID
    programmer_id: Optional[uuid.UUID] = None
    tester_id: uuid.UUID


class BoxAccountingResponse(BoxAccountingBase):
    scheme_developer: PersonBase
    assembler: PersonBase
    programmer: Optional[PersonBase] = None
    tester: PersonBase

    class Config:
        orm_mode = True


class PaginatedBoxAccounting(BaseModel):
    items: List[BoxAccountingResponse]
    total: int
    page: int
    size: int
    pages: int
