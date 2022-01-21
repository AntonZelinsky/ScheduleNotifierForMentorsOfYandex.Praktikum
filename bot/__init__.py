import datetime
import logging
from queue import Queue
from threading import Thread

import telegram.ext
from pytz import timezone
from telegram import ParseMode, Bot
from telegram.ext import (CallbackContext,
                          Updater,
                          Dispatcher,
                          JobQueue,
                          Defaults)

import notion
from app.services import CohortService
from core import config
from core.database import SessionLocal
from handlers.conversation_handlers import registration_conv
from helpers import Objectify

settings = config.get_settings()


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет, {update.effective_chat.full_name}, "
                                  "я буду присылать тебе уведомления о дежурстве в Я.П, "
                                  f"твой telegram id *{update.effective_chat.id}*.", parse_mode=ParseMode.MARKDOWN)
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')


service: CohortService = CohortService(SessionLocal())


def callback_morning_reminder(context: CallbackContext):
    cohorts = service.get_cohorts()
    users = notion.get_users_data(cohorts)

    for user_data in users.values():
        user = Objectify(user_data)
        if user.telegram_id:
            # TODO Как сделать наличие telegram_id гарантированным?
            # или будут разные каналы доставки?
            # пока добавил __getattr__ в class Expando
            context.bot.send_message(chat_id=user.telegram_id,
                                     text=f'Доброе утро, {user.name}. Напоминаю, ты сегодня дежуришь.\n'
                                          f'В {" и ".join([cohort.name for cohort in user.databases])}\n\n'
                                          'Желаю хорошего дня!')
            logging.info(f'{user.name} c id {user.telegram_id} получил утреннее напоминание о дежурстве')


def callback_evening_reminder(context: CallbackContext):
    cohorts = service.get_cohorts()
    users = notion.get_users_data(cohorts)

    for user_data in users.values():
        user = Objectify(user_data)
        if user.telegram_id:
            context.bot.send_message(chat_id=user.telegram_id,
                                     text=f'Добрый вечер, {user.name}. Ещё раз напоминаю, ты сегодня дежуришь.\n'
                                          f'В {" и ".join([cohort.name for cohort in user.databases])}\n\n'
                                          'Спокойной ночи!')
            logging.info(f'{user.name} c id {user.telegram_id} получил вечернее напоминание о дежурстве')


def init_webhook(token, webhook_url, defaults: Defaults):
    bot = Bot(token, defaults=defaults)
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


def init_polling(token, defaults: Defaults):
    updater = Updater(token, use_context=True, defaults=defaults)
    updater.start_polling()

    logging.info('Приложение успешно запущено через пулинг')
    return updater.dispatcher


def init():
    token = settings.telegram_token
    # Defining timezone of a bot for all datetime references (default is UTC)
    defaults = telegram.ext.Defaults(tzinfo=timezone("Europe/Warsaw"))
    if settings.domain_address:
        webhook_url = f'{settings.domain_address}/{token}/telegramWebhook'
        dispatcher = init_webhook(token, webhook_url, defaults)
    else:
        dispatcher = init_polling(token, defaults)

    time = datetime.datetime.strptime(settings.morning_reminder_hour, "%H:%M").time()
    dispatcher.job_queue.run_daily(callback_morning_reminder, time)

    time = datetime.datetime.strptime(settings.evening_reminder_hour, "%H:%M").time()
    dispatcher.job_queue.run_daily(callback_evening_reminder, time)

    dispatcher.add_handler(registration_conv)

    return dispatcher
