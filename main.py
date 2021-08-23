import logging

import dotenv

dotenv.load_dotenv()

import bot

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    bot.init()
