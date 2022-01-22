import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    telegram_id = Column(Integer)
    notion_user_id = Column(UUID(as_uuid=True), unique=True)
    is_activated = Column(Boolean, default=False)
    created = Column(DateTime(), default=datetime.now)
    modified = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Cohort(Base):
    __tablename__ = "Cohorts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    notion_db_id = Column(UUID(as_uuid=True), unique=True)

    def __repr__(self):
        return f'{self.id}: {self.name} {self.notion_db_id}'


class Registrations(Base):
    __tablename__ = "Registrations"

    confirmation_code = Column(UUID(as_uuid=True),
                               primary_key=True, default=uuid.uuid4)
    telegram_id = Column(Integer, index=True)
    name = Column(String)
    email = Column(String, unique=False, index=True)
    archived = Column(Boolean, default=False)
    created = Column(DateTime(), default=datetime.now)
    modified = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
