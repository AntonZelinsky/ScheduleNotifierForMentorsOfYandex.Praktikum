from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import services
from core.database import get_db

from .. import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Cohort], tags=['Cohorts'])
def read_cohorts(
          skip: int = 0,
          limit: int = 100,
          db: Session = Depends(get_db),
):
    cohorts = services.get_cohorts(db, skip=skip, limit=limit)
    return cohorts


@router.post("/", response_model=schemas.Cohort, tags=['Cohorts'])
def create_cohort(
          cohort: schemas.CohortCreate,
          db: Session = Depends(get_db),
):
    db_cohort = services.get_cohort_by_name(db, name=cohort.name)
    if db_cohort:
        raise HTTPException(
            status_code=400,
            detail="Cohort already added",
        )
    return services.create_cohort(db=db, cohort=cohort)
