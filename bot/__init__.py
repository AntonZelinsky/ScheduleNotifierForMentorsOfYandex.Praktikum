import datetime
import logging
from queue import Queue
from threading import Thread

from pytz import timezone
from telegram import ParseMode, Bot
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          Updater,
                          Dispatcher,
                          JobQueue)

import notion
from helpers import Objectify
from ..core import config


settings = config.get_settings()


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет, {update.effective_chat.full_name}, "
                                  "я буду присылать тебе уведомления о дежурстве в Я.П, "
                                  f"твой telegram id *{update.effective_chat.id}*.", parse_mode=ParseMode.MARKDOWN)
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')


def callback_morning_reminder(context: CallbackContext):
    users = notion.get_users_data()
    for user_data in users.values():
        user = Objectify(user_data)
        if user.telegram_id:
            # TODO Как сделать наличие telegram_id гарантированным?
            # или будут разные каналы доставки?
            # пока добавил __getattr__ в class Expando
            context.bot.send_message(chat_id=user.telegram_id,
                                     text=f'Доброе утро, {user.name}. Напоминаю, ты сегодня дежуришь.\n'
                                          f'В {user.database_ids}\n\n'
                                          'Желаю хорошего дня!')
            logging.info(f'{user.name} c id {user.telegram_id} получил утреннее напоминание о дежурстве')


def callback_evening_reminder(context: CallbackContext):
    users = notion.get_users_data()
    for user_data in users.values():
        user = Objectify(user_data)
        if user.telegram_id:
            context.bot.send_message(chat_id=user.telegram_id,
                                     text=f'Добрый вечер, {user.name}. Ещё раз напоминаю, ты сегодня дежуришь.\n'
                                          f'В {user.database_ids}\n\n'
                                          'Спокойной ночи!')
            logging.info(f'{user.name} c id {user.telegram_id} получил вечернее напоминание о дежурстве')


def init_webhook(token, webhook_url):
    bot = Bot(token)
    update_queue = Queue()
    job_queue = JobQueue()
    dispatcher = Dispatcher(bot, update_queue, job_queue=job_queue)
    job_queue.set_dispatcher(dispatcher)

    success_setup = bot.set_webhook(webhook_url)
    if not success_setup:
        raise AttributeError("Cannot set up telegram webhook")
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    logging.info('Приложение работает через вебхук')
    return dispatcher


def init_pooling(token):
    updater = Updater(token, use_context=True)
    updater.start_polling()

    logging.info('Приложение успешно запущено через пулинг')
    return updater.dispatcher


def init():
    token = settings.telegram_token
    webhook_url = f'{settings.domain_address}/{token}/telegramWebhook'
    if webhook_url:
        dispatcher = init_webhook(token, webhook_url)
    else:
        dispatcher = init_pooling(token)

    time = datetime.time(hour=settings.morning_reminder_hour, tzinfo=timezone("Europe/Warsaw"))
    dispatcher.job_queue.run_daily(callback_morning_reminder, time)

    time = datetime.time(hour=settings.evening_reminder_hour, tzinfo=timezone("Europe/Warsaw"))
    dispatcher.job_queue.run_daily(callback_evening_reminder, time)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    return dispatcher
