from uuid import UUID

from fastapi import HTTPException

from core import models

from . import schemas


class UserService:
    @staticmethod
    def has_user_by_telegram_id(db, telegram_id: int) -> bool:
        return not db.query(models.User).filter(
            models.User.telegram_id == telegram_id).first() is None

    @staticmethod
    def get_users(db, skip: int = 0, limit: int = 100):
        return db.query(models.User).offset(skip).limit(limit).all()

    def create_user(self, db, user: schemas.UserCreate):
        """Создать юзера в БД, если еще нет юзера с таким телеграм_ид."""
        if self.has_user_by_telegram_id(db, telegram_id=user.telegram_id):
            raise HTTPException(status_code=400,
                                detail='User already registered')
        db_user = models.User(name=user.name, telegram_id=user.telegram_id)
        db.add(db_user)
        db.commit()
        return db_user


class CohortService:
    @staticmethod
    def get_cohorts(db, skip: int = 0, limit: int = 100):
        return db.query(models.Cohort).offset(skip).limit(limit).all()

    @staticmethod
    def has_cohort_by_uuid(db, uuid: UUID) -> bool:

        return db.query(models.Cohort).filter(
            models.Cohort.notion_db_id == uuid,
        ).first()

    def create_cohort(self, db, cohort: schemas.CohortCreate):
        """Создать когорту в БД, если еще нет когорты с таким uuid."""
        if self.has_cohort_by_uuid(db, cohort.notion_db_id):
            raise HTTPException(status_code=400, detail='Cohort already added')
        db_cohort = models.Cohort(
            name=cohort.name,
            notion_db_id=cohort.notion_db_id,
        )
        db.add(db_cohort)
        db.commit()
        return db_cohort
