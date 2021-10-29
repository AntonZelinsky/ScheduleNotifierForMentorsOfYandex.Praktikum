from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    telegram_id: int
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_activated: bool
    email: Optional[EmailStr] = None
    notion_user_id: Optional[UUID] = None
    created: datetime
    modified: datetime

    class Config:
        orm_mode = True


class CohortBase(BaseModel):
    name: str
    notion_db_id: UUID


class CohortCreate(CohortBase):
    pass


class Cohort(CohortBase):
    id: int

    class Config:
        orm_mode = True
