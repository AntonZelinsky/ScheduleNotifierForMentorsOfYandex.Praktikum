import logging

import dotenv

import bot

if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    bot.init()
