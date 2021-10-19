import uvicorn

from fastapi import FastAPI

from .api import router


# models.Base.metadata.create_all(bind=engine)

def create_app() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


app = create_app()


@app.post('/{token}/telegramWebhook')
def webhook():
    """Эндпойнт, на который  приходят обновления из ТГ"""
    return {'telegram': 'webhook'}


# вынести в отдельный файл
def run_uvicorn():
    uvicorn.run(app, host='0.0.0.0', port=80)
