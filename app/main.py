from fastapi import FastAPI
from pydantic import BaseModel
from telegram import Update

import bot
from .api import router
from .config import config


settings = config['test']()

def create_app() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


app = create_app()

dispatcher = bot.init()

@app.post('/{token}/telegramWebhook')
def webhook(data: dict):
    update = Update.de_json(data, dispatcher.bot)
    dispatcher.process_update(update)


# тестоый эндпойнт для просмотра настроек
@app.get('/settings')
def get_settings():
    return settings
