import uvicorn

from fastapi import FastAPI, Request

import notion


app = FastAPI()

# main webhook. Telegram posts json to this addres -> decode json -> check message value -> select handler based on the message 
@app.post("/")
async def start_webhook(request: Request):
    return {"received_request_body": await request.body()}
    # Decode JSON and insert handlers here


# запрашиваем данные по сегодняшнему дежурному в определенной когорте
@app.get("/on_duty")
def fetch_notion_data():
    data = notion.get_user_data()
    return data

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
