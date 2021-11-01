from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from app.services import CohortService
from core.database import get_db

from .. import schemas

router = InferringRouter()


@cbv(router)
class CohortCBV:
    db: Session = Depends(get_db)

    @router.get("/", response_model=List[schemas.Cohort])
    def read_cohorts(self, skip: int = 0, limit: int = 100):
        return CohortService.get_cohorts(self.db, skip=skip, limit=limit)

    @router.post("/", response_model=schemas.Cohort)
    def create_cohort(self, cohort: schemas.CohortCreate):
        return CohortService.create_cohort(db=self.db, cohort=cohort)
