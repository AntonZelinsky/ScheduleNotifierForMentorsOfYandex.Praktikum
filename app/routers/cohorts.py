from typing import List

from fastapi import Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

import notion
from app import services
from core.database import get_db

from .. import schemas

router = InferringRouter()


@cbv(router)
class CohortCBV:
    db: Session = Depends(get_db)

    @router.get("/", response_model=List[schemas.Cohort], tags=['Cohorts'])
    def read_cohorts(
              self,
              skip: int = 0,
              limit: int = 100,
    ):
        cohorts = services.get_cohorts(self.db, skip=skip, limit=limit)
        return cohorts

    @router.post("/", response_model=schemas.Cohort, tags=['Cohorts'])
    def create_cohort(
              self,
              cohort: schemas.CohortCreate,
    ):
        db_cohort = services.get_cohort_by_name(self.db, name=cohort.name)
        if db_cohort:
            raise HTTPException(
                status_code=400,
                detail="Cohort already added",
            )
        created_cohort = services.create_cohort(db=self.db, cohort=cohort)
        created_calendar_database = notion.create_calendar_database(
            cohort=created_cohort,
        )
        created_cohort.notion_db_id = created_calendar_database.id
        return services.set_cohort_notion_id(db=self.db, cohort=created_cohort)
