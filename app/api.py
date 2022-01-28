from fastapi import APIRouter

from app.routers import cohorts, users

router = APIRouter()
router.include_router(users.router, tags=["Users"], prefix="/users")
router.include_router(cohorts.router, tags=["Cohorts"], prefix="/cohorts")
