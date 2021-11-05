from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.services import CohortService

from .. import schemas

router = InferringRouter()


@cbv(router)
class CohortCBV:

    @router.get("/", response_model=List[schemas.Cohort])
    def read_cohorts(self, service: CohortService = Depends()):
        return service.get_cohorts(skip=service.skip, limit=service.limit)

    @router.post("/", response_model=schemas.Cohort)
    def create_cohort(self,
                      cohort: schemas.CohortCreate,
                      service: CohortService = Depends(),
                      ):
        return service.create_cohort(cohort=cohort)
