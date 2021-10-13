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
    email: str
    notion_us_id: str

    class Config:
        orm_mode = True


class FacultyBase(BaseModel):
    name: str


class FacultyCreate(FacultyBase):
    pass


class Faculty(FacultyBase):
    id: int

    class Config:
        orm_mode = True


class CohortBase(BaseModel):
    number: int


class CohortCreate(CohortBase):
    faculty_id: int


class Cohort(CohortBase):
    id: int
    faculty_id: int
    notion_db_id: Optional[str] = None

    class Config:
        orm_mode = True
