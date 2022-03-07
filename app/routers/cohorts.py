from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app import schemas
from app.services import CohortService
from core.services.notion_services import NotionServices

router = InferringRouter()
notion_services = NotionServices()


@cbv(router)
class CohortCBV:
    service: CohortService = Depends()
    skip: int = 0
    limit: int = 100

    @router.get("/", response_model=List[schemas.Cohort])
    def read_cohorts(self):
        return self.service.get_cohorts(skip=self.skip, limit=self.limit)

    @router.post("/", response_model=schemas.Cohort)
    def create_cohort(self, cohort: schemas.CohortCreate):
        return self.service.create_cohort(cohort=cohort)
