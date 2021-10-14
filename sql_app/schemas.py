from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_activated: bool
    email: Optional[str] = None
    notion_us_id: Optional[str] = None
    created: datetime
    modified: datetime

    class Config:
        orm_mode = True


class CohortBase(BaseModel):
    name: str


class CohortCreate(CohortBase):
    pass


class Cohort(CohortBase):
    id: int
    notion_db_id: Optional[str] = None

    class Config:
        orm_mode = True
