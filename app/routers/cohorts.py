from typing import List

from fastapi import Depends
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
    def read_cohorts(self, skip: int = 0, limit: int = 100):
        cohorts = services.get_cohorts(self.db, skip=skip, limit=limit)
        return cohorts

    @router.get("/sync/", response_model=List, tags=['Cohorts'])
    def sync_cohorts(self):
        return notion.sync_notion_databases_to_db(self.db)
