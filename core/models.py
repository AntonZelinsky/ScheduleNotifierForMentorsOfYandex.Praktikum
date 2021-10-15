from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from sql_app.database import Base


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    telegram_id = Column(Integer)
    notion_user_id = Column(String)
    is_activated = Column(Boolean, default=False)
    created = Column(DateTime(), default=datetime.now)
    modified = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Cohort(Base):
    __tablename__ = "Cohorts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    notion_db_id = Column(String)
