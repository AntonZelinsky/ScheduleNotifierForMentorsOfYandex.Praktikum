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


@app.get("/faculties/", response_model=List[schemas.Faculty])
def read_faculties(
          skip: int = 0,
          limit: int = 100,
          db: Session = Depends(get_db),
):
    faculties = crud.get_faculties(db, skip=skip, limit=limit)
    return faculties


@app.post("/faculties/", response_model=schemas.Faculty)
def create_faculty(
          faculty: schemas.FacultyCreate,
          db: Session = Depends(get_db),
):
    db_faculty = crud.get_faculty_by_name(db, name=faculty.name)
    if db_faculty:
        raise HTTPException(
            status_code=400,
            detail="Faculty already added",
        )
    return crud.create_faculty(db=db, faculty=faculty)


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
    db_cohort = crud.get_cohort_by_faculty_id_and_number(
        db,
        faculty_id=cohort.faculty_id,
        number=cohort.number,
    )
    if db_cohort:
        raise HTTPException(
            status_code=400,
            detail="Cohort already added",
        )
    return crud.create_cohort(db=db, cohort=cohort)
