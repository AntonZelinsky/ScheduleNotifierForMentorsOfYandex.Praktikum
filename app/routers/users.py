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
class UserCBV:
    db: Session = Depends(get_db)

    @router.get("/", response_model=List[schemas.User])
    def read_users(self, skip: int = 0, limit: int = 100):
        users = services.get_users(self.db, skip=skip, limit=limit)
        return users

    @router.post("/", response_model=schemas.User)
    def create_user(self, user: schemas.UserCreate):
        try:
            user = services.create_user(db=self.db, user=user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f'{e}')
        return user
