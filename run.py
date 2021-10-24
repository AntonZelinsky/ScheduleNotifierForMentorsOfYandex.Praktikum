import logging

import dotenv
import uvicorn

dotenv.load_dotenv()
import bot
from app import main


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # bot.init()
    uvicorn.run(main.app, host='127.0.0.1', port=8888)
