from fastapi import FastAPI

from core import models
from core.database import engine

from .api import router

models.Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


app = create_app()
