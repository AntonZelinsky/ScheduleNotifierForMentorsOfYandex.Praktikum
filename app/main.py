import os
import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel
from telegram import Update

import bot
from .api import router
from core import models
from core.database import engine

# models.Base.metadata.create_all(bind=engine)

# создаем модель для сообщения, получаемого с сервера ТГ
class Message(BaseModel):
    update_id: int
    message: dict


def create_app() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


app = create_app()

# в таком виде dispatcher возвращается как NoneType
dispatcher = bot.init()

@app.post('/{token}/telegramWebhook')
def webhook(update: dict):
    """Эндпойнт, на который  приходят обновления из ТГ"""
    update = Update.de_json(update, dispatcher)
    dispatcher.process_update(update)
    # return(update['message']['text'])


# TODO вынести в отдельный файл
def run_uvicorn():
    uvicorn.run(app, host='0.0.0.0', port=80)
