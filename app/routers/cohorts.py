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
    service: CohortService = Depends()
    db: Session = Depends(get_db)
    skip: int = 0
    limit: int = 100

    @router.get("/", response_model=List[schemas.Cohort])
    def read_cohorts(self):
        return self.service.get_cohorts(self.db, skip=self.skip,
                                        limit=self.limit)

    @router.post("/", response_model=schemas.Cohort)
    def create_cohort(self, cohort: schemas.CohortCreate):
        return self.service.create_cohort(self.db, cohort=cohort)
