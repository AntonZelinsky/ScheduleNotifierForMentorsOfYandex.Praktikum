from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

import notion
from app.services import CohortService

from .. import schemas

router = InferringRouter()


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

    @router.get("/cycle")
    def cycle(self):
        cohorts = self.service.get_cohorts(skip=self.skip, limit=self.limit)
        # for cohort in cohorts:
        last_duties = notion.get_last_duties_by_cohort(cohorts[1])
        cycle = notion.calculate_cycle_by_last_duties(last_duties['last_mentors_ids'])
        added_duties = notion.add_duties_to_cohort(cohorts[1], cycle, last_duties['actual_date'])
        return added_duties
