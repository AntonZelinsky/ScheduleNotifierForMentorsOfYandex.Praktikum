from sqlalchemy.orm import Session

from app import schemas
from core import models


def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(models.User).filter(
        models.User.telegram_id == telegram_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, telegram_id=user.telegram_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_cohorts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cohort).offset(skip).limit(limit).all()


def get_cohort_by_name(db: Session, name: str):
    return db.query(models.Cohort).filter(
        models.Cohort.name == name,
    ).first()


def create_cohort(db: Session, cohort: schemas.CohortCreate):
    db_cohort = models.Cohort(name=cohort.name)
    db.add(db_cohort)
    db.commit()
    db.refresh(db_cohort)
    return db_cohort


def set_cohort_notion_id(db: Session, cohort: schemas.Cohort):
    db_cohort = db.query(models.Cohort).get(cohort.id)
    db_cohort.notion_db_id = cohort.notion_db_id
    db.commit()
    db.refresh(db_cohort)
    return db_cohort
