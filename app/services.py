from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from core import models
from core.config import get_settings
from core.database import get_db
from core.mail import send_email

from app import schemas

settings = get_settings()


class Services:
    def __init__(self,
                 background_tasks: BackgroundTasks,
                 db: Session = Depends(get_db),
                 ):
        self.db = db
        self.background_tasks = background_tasks


class UserService(Services):
    def has_user_by_telegram_id(self, telegram_id: int) -> bool:
        return not self.db.query(models.User).filter(
            models.User.telegram_id == telegram_id).first() is None

    def get_user_by_email(self, email: EmailStr):
        return self.db.query(models.User).filter(models.User.email == email).first()

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
        self.set_registration_obsolete(telegram_id=registration.telegram_id)
        registration = models.Registrations(
            name=registration.name,
            email=registration.email,
            telegram_id=registration.telegram_id,
        )
        self.db.add(registration)
        self.db.commit()
        self.send_confirmation_code(registration)
        return registration

    def set_registration_obsolete(self, telegram_id: int):
        """Отметить устаревшими прошлые регистрации пользователя."""
        self.db.query(models.Registrations).filter(
            models.Registrations.telegram_id == telegram_id
        ).update({'archived': True}, synchronize_session='fetch')

    def send_confirmation_code(self, registration: schemas.Registration):
        """Отправить письмо с кодом/ссылкой подтверждения регистрации."""
        email = registration.email
        subject = 'Нужно подтверждение регистрации в боте Яндекс.Практикума'
        template_body = dict(
            link=f'https://{settings.domain_address}?'
                 f'start={registration.confirmation_code}'
        )
        send_email(
            self.background_tasks,
            recipients=[email],
            subject=subject,
            template_body=template_body,
            template_html='registration_confirmation.html',
        )

    def get_user_by_notion_id(self, notion_user_id: UUID):
        return self.db.query(models.User).filter_by(notion_user_id=notion_user_id).first()


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
