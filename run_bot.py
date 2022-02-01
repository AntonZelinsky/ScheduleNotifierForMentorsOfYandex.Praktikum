import logging

import dotenv
from telegram.ext import Updater

import bot

dotenv.load_dotenv()

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    u = bot.init()
    if isinstance(u, Updater):
        u.idle()
