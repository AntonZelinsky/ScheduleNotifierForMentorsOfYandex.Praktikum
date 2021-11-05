from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.services import UserService

from .. import schemas

router = InferringRouter()


@cbv(router)
class UserCBV:

    @router.get("/", response_model=List[schemas.User])
    def read_users(self, service: UserService = Depends()):
        return service.get_users(skip=service.skip, limit=service.limit)

    @router.post("/", response_model=schemas.User)
    def create_user(self,
                    user: schemas.UserCreate,
                    service: UserService = Depends()
                    ):
        return service.create_user(user=user)
