from fastapi import APIRouter

from .routes import cohorts, users

router = APIRouter()
router.include_router(users.router, tags=["Users"], prefix="/users")
router.include_router(cohorts.router, tags=["Cohorts"], prefix="/cohorts")
