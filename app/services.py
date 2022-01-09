from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from core import models
from core.database import get_db

from . import schemas


class Services:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db


class UserService(Services):
    def has_user_by_telegram_id(self, telegram_id: int) -> bool:
        return not self.db.query(models.User).filter(
            models.User.telegram_id == telegram_id).first() is None

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create_user(self, user: schemas.UserCreate):
        """Создать юзера в БД, если еще нет юзера с таким телеграм_ид."""
        if self.has_user_by_telegram_id(telegram_id=user.telegram_id):
            raise HTTPException(status_code=400,
                                detail='User already registered')
        db_user = models.User(name=user.name, telegram_id=user.telegram_id)
        self.db.add(db_user)
        self.db.commit()
        return db_user

    def create_registration(self, registration: schemas.RegistrationCreate):
        """Создать "заявку" на добавление пользователя."""
        self.set_registration_obsolete(telegram_id=registration.id)
        registration = models.Registrations(
            name=registration.name,
            email=registration.email,
            id=registration.id,
        )
        self.db.add(registration)
        self.db.commit()
        print(self.send_confirmation_code(registration))
        return registration

    def set_registration_obsolete(self, telegram_id: int):
        """Отметить устаревшими прошлые регистрации пользователя."""
        self.db.query(models.Registrations).filter(
            models.Registrations.id == telegram_id
        ).update({"is_obsolete": True}, synchronize_session="fetch")

    def send_confirmation_code(self, registration: schemas.Registration):
        """Отправить письмо с кодом/ссылкой подтверждения регистрации."""
        email = registration.email
        text = f'Перейдите по ссылке: <a href="#">{registration.uuid}</a>'
        return text


class CohortService(Services):
    def get_cohorts(self, skip: int = 0, limit: int = 100):
        return self.db.query(models.Cohort).offset(skip).limit(limit).all()

    def has_cohort_by_uuid(self, uuid: UUID) -> bool:

        return self.db.query(models.Cohort).filter(
            models.Cohort.notion_db_id == uuid,
        ).first()

    def create_cohort(self, cohort: schemas.CohortCreate):
        """Создать когорту в БД, если еще нет когорты с таким uuid."""
        if self.has_cohort_by_uuid(cohort.notion_db_id):
            raise HTTPException(status_code=400, detail='Cohort already added')
        db_cohort = models.Cohort(
            name=cohort.name,
            notion_db_id=cohort.notion_db_id,
        )
        self.db.add(db_cohort)
        self.db.commit()
        return db_cohort
