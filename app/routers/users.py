from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from app.services import UserService
from core.database import get_db

from .. import schemas

router = InferringRouter()


@cbv(router)
class UserCBV:
    db: Session = Depends(get_db)

    @router.get("/", response_model=List[schemas.User])
    def read_users(self, skip: int = 0, limit: int = 100):
        return UserService.get_users(self.db, skip=skip, limit=limit)

    @router.post("/", response_model=schemas.User)
    def create_user(self, user: schemas.UserCreate):
        return UserService.create_user(db=self.db, user=user)
