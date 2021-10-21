import uvicorn

from fastapi import FastAPI, Request
from queue import Queue

import notion


app = FastAPI()

@app.post('/telegramWebhook')
async def webhook(update):
    """Эндпойнт, на который  приходят обновления из ТГ"""
    update_queue = Queue()
    return {'update_received': update_queue.put(update)}
    # Возвращаем расшифрованный объект Update если приложение работет через вебхуки


# запрашиваем данные по сегодняшнему дежурному в определенной когорте
@app.get('/on_duty')
def fetch_notion_data():
    data = notion.get_user_data()
    return data


# вынести в отдельный файл
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
