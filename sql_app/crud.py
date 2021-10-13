from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


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


def get_faculties(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Faculty).offset(skip).limit(limit).all()


def get_faculty_by_name(db: Session, name: str):
    return db.query(models.Faculty).filter(models.Faculty.name == name).first()


def create_faculty(db: Session, faculty: schemas.FacultyCreate):
    db_faculty = models.Faculty(name=faculty.name)
    db.add(db_faculty)
    db.commit()
    db.refresh(db_faculty)
    return db_faculty


def get_cohort_by_faculty_id_and_number(db: Session, faculty_id: int,
                                        number: int, ):
    return db.query(models.Cohort).filter(
        models.Cohort.faculty_id == faculty_id,
        models.Cohort.number == number,
    ).first()


def get_cohorts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cohort).offset(skip).limit(limit).all()


def create_cohort(db: Session, cohort: schemas.CohortCreate):
    db_cohort = models.Cohort(
        number=cohort.number,
        faculty_id=cohort.faculty_id,
    )
    db.add(db_cohort)
    db.commit()
    db.refresh(db_cohort)
    return db_cohort
