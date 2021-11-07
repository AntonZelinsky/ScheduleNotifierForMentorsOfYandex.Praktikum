from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.services import UserService

from .. import schemas

router = InferringRouter()


@cbv(router)
class UserCBV:
    service: UserService = Depends()
    skip: int = 0
    limit: int = 100

    @router.get("/", response_model=List[schemas.User])
    def read_users(self):
        return self.service.get_users(skip=self.skip, limit=self.limit)

    @router.post("/", response_model=schemas.User)
    def create_user(self, user: schemas.UserCreate):
        return self.service.create_user(user=user)
