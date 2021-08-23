import datetime
import logging
import os

from pytz import timezone
from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.ext import Updater, CallbackContext

import notion

token = os.getenv('TELEGRAM_TOKEN')


def callback_morning_remainder(context: CallbackContext):
    user = notion.get_user_data()

    context.bot.send_message(chat_id=user.telegram_id,
                             text=f'Привет, {user.name}. Напоминаю, ты сегодня дежуришь.')
    logging.info(f'{user.name} c id {user.telegram_id} получил уведомление о дежурстве')


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет, {update.effective_chat.full_name}, "
                                  "я буду присылать тебе уведомления о дежурстве в Я.П, "
                                  f"твой telegram id *{update.effective_chat.id}*.", parse_mode=ParseMode.MARKDOWN)
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')


def init():
    updater = Updater(token, use_context=True)

    time = datetime.time(hour=9, minute=0, tzinfo=timezone("Europe/Warsaw"))
    _job_daily = updater.job_queue.run_daily(callback_morning_remainder, time)

    start_handler = CommandHandler('start', start)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)

    logging.info("Приложение успешно запущено")
    updater.start_polling()
