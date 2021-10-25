from fastapi import FastAPI
from telegram import Update

import bot
from .config import BaseConfig
from .api import router


def create_app() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


app = create_app()

dispatcher = bot.init()

settings = BaseConfig()

@app.post('/{token}/telegramWebhook')
def webhook(data: dict):
    update = Update.de_json(data, dispatcher.bot)
    dispatcher.process_update(update)


@app.get('/settings')
def get_settings():
    return {'settings': settings}
