from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.services import UserService

from app import schemas

router = InferringRouter()


@cbv(router)
class UserCBV:
    service: UserService = Depends()
    skip: int = 0
    limit: int = 100

    @router.get("/", response_model=List[schemas.User])
    def read_users(self):
        return self.service.get_users(skip=self.skip, limit=self.limit)

    @router.post("/", response_model=schemas.Registration)
    def create_registration(self, user: schemas.RegistrationCreate):
        return self.service.create_registration(registration=user)
