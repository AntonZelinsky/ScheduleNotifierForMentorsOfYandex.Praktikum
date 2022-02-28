import logging

from fastapi import FastAPI
from telegram import Update

import bot

from app.api import router

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


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
