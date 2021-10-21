import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel

from .api import router


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


@app.post('/{token}/telegramWebhook')
def webhook(update: Message):
    """Эндпойнт, на который  приходят обновления из ТГ"""
    text = update.message['text']
    print(text)
    # Как сюда добавить созданный экземпляр бота и хэндлер? 
    return {'telegram': text}


# TODO вынести в отдельный файл
def run_uvicorn():
    uvicorn.run(app, host='0.0.0.0', port=80)
