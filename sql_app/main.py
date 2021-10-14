from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/", response_model=List[schemas.User])
def read_users(
          skip: int = 0,
          limit: int = 100,
          db: Session = Depends(get_db),
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="User already registered",
        )
    return crud.create_user(db=db, user=user)


@app.get("/cohorts/", response_model=List[schemas.Cohort])
def read_cohorts(
          skip: int = 0,
          limit: int = 100,
          db: Session = Depends(get_db),
):
    cohorts = crud.get_cohorts(db, skip=skip, limit=limit)
    return cohorts


@app.post("/cohorts/", response_model=schemas.Cohort)
def create_cohort(
          cohort: schemas.CohortCreate,
          db: Session = Depends(get_db),
):
    db_cohort = crud.get_cohort_by_name(db, name=cohort.name)
    if db_cohort:
        raise HTTPException(
            status_code=400,
            detail="Cohort already added",
        )
    return crud.create_cohort(db=db, cohort=cohort)
