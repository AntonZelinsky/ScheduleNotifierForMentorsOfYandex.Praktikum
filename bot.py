import datetime
import logging
import os

from pytz import timezone
from telegram import ParseMode
from telegram.ext import CallbackContext, CommandHandler, Updater

import notion
from helpers import Objectify


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет, {update.effective_chat.full_name}, "
                                  "я буду присылать тебе уведомления о дежурстве в Я.П, "
                                  f"твой telegram id *{update.effective_chat.id}*.", parse_mode=ParseMode.MARKDOWN)
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')


def callback_morning_remainder(context: CallbackContext):
    users = notion.get_users_data()
    for email, user_data in users.items():
        user = Objectify(user_data)
        if user.telegram_id:
            # TODO Как сделать наличие telegram_id гарантированным?
            # или будут разные каналы доставки?
            # пока добавил __getattr__ в class Expando
            context.bot.send_message(chat_id=user.telegram_id,
                                     text=f'Доброе утро, {user.name}. Напоминаю, ты сегодня дежуришь.\n'
                                          f'в {user.database_ids}\n\n'
                                          'Желаю хорошего дня!')
            logging.info(f'{user.name} c id {user.telegram_id} получил утреннее напоминание о дежурстве')


def callback_evening_remainder(context: CallbackContext):
    users = notion.get_users_data()
    for email, user_data in users.items():
        user = Objectify(user_data)
        if user.telegram_id:
            context.bot.send_message(chat_id=user.telegram_id,
                                     text=f'Добрый вечер, {user.name}. Ещё раз напоминаю, ты сегодня дежуришь.\n'
                                          f'в {user.database_ids}\n\n'
                                          'Спокойной ночи!')
            logging.info(f'{user.name} c id {user.telegram_id} получил вечернее напоминание о дежурстве')


def init():
    token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(token, use_context=True)

    morning_remainder_hour = int(os.getenv('MORNING_REMAINDER_HOUR', int))
    time = datetime.time(hour=morning_remainder_hour, tzinfo=timezone("Europe/Moscow"))
    updater.job_queue.run_daily(callback_morning_remainder, time)

    evening_remainder_hour = int(os.getenv('EVENING_REMAINDER_HOUR', int))
    time = datetime.time(hour=evening_remainder_hour, tzinfo=timezone("Europe/Moscow"))
    updater.job_queue.run_daily(callback_evening_remainder, time)

    start_handler = CommandHandler('start', start)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)

    logging.info("Приложение успешно запущено")
    updater.start_polling()
    updater.idle()
