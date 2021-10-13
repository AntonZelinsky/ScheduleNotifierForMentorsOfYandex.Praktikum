from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    telegram_id = Column(Integer)
    notion_us_id = Column(String)
    is_activated = Column(Boolean, default=False)
    created = Column(DateTime(), default=datetime.now)
    modified = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Cohort(Base):
    __tablename__ = "Cohorts"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    faculty_id = Column(Integer, ForeignKey("Faculty.id"))
    notion_db_id = Column(String)

    faculty = relationship("Faculty", back_populates="cohorts")


class Faculty(Base):
    __tablename__ = "Faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    cohorts = relationship("Cohort", back_populates="faculty")
