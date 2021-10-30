from typing import List

from fastapi import Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from app import services
from core.database import get_db

from .. import schemas

router = InferringRouter()


@cbv(router)
class CohortCBV:
    db: Session = Depends(get_db)

    @router.get("/", response_model=List[schemas.Cohort], tags=['Cohorts'])
    def read_cohorts(self, skip: int = 0, limit: int = 100):
        cohorts = services.get_cohorts(self.db, skip=skip, limit=limit)
        return cohorts

    @router.post("/", response_model=schemas.Cohort)
    def create_cohort(self, cohort: schemas.CohortCreate):
        try:
            cohort = services.create_cohort(db=self.db, cohort=cohort)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f'{e}')
        return cohort
