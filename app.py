import uvicorn

from fastapi import FastAPI

import notion

app = FastAPI()

# корневой вебхук
@app.get("/")
def start_webhook():
    return{"Telegram bot": "Base Webhook"}

# запрашиваем данные по сегодняшнему дежурному в определенной когорте
@app.get("/on_duty")
def fetch_notion_data():
    data = notion.get_user_data()
    return data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
