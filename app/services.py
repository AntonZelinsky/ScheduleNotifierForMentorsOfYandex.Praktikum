from sqlalchemy.orm import Session

from app import schemas
from core import models


def has_user_by_telegram_id(db: Session, telegram_id: int) -> bool:
    return not db.query(models.User).filter(
        models.User.telegram_id == telegram_id).first() is None


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    """Создать юзера в БД, если еще нет юзера с таким телеграм_ид."""
    if has_user_by_telegram_id(db, telegram_id=user.telegram_id):
        raise ValueError("User already registered")
    db_user = models.User(name=user.name, telegram_id=user.telegram_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_cohorts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cohort).offset(skip).limit(limit).all()


def has_cohort_by_uuid(db: Session, uuid: str) -> bool:
    return db.query(models.Cohort).filter(
        models.Cohort.notion_db_id == uuid,
    ).first()


def create_cohort(db: Session, cohort: schemas.CohortCreate):
    """Создать когорту в БД, если еще нет когорты с таким uuid."""
    # TODO. FIX: uuid передается в виде строки, иначе какая-то проблема.
    if has_cohort_by_uuid(db, str(cohort.notion_db_id)):
        raise ValueError("Cohort already added")
    db_cohort = models.Cohort(
        name=cohort.name,
        notion_db_id=cohort.notion_db_id,
    )
    db.add(db_cohort)
    db.commit()
    db.refresh(db_cohort)
    return db_cohort
