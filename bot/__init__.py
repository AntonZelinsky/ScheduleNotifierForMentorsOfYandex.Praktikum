import logging
from queue import Queue
from threading import Thread

import telegram.ext
from pytz import timezone
from telegram import Bot, ParseMode
from telegram.ext import Defaults, Dispatcher, JobQueue, Updater

from bot import jobs_callbacks
from core import config
from handlers.conversation_handlers import registration_conv
from helpers import str_to_time

settings = config.get_settings()


def init_webhook(token, webhook_url, defaults: Defaults):
    bot = Bot(token, defaults=defaults)
    update_queue = Queue()
    job_queue = JobQueue()
    dispatcher = Dispatcher(bot, update_queue, job_queue=job_queue)
    job_queue.set_dispatcher(dispatcher)

    success_setup = bot.set_webhook(webhook_url)
    if not success_setup:
        raise AttributeError('Cannot set up telegram webhook')
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

    defaults = telegram.ext.Defaults(tzinfo=timezone(settings.timezone))
    if settings.domain_address:
        webhook_url = f'{settings.domain_address}/{token}/telegramWebhook'
        dispatcher = init_webhook(token, webhook_url, defaults)
    else:
        dispatcher = init_polling(token, defaults)

    dispatcher.job_queue.run_daily(
        callback=jobs_callbacks.morning_reminder_callback,
        time=str_to_time(settings.morning_reminder_hour),
    )

    dispatcher.job_queue.run_daily(
        callback=jobs_callbacks.evening_reminder_callback,
        time=str_to_time(settings.evening_reminder_hour),
    )

    dispatcher.job_queue.run_daily(
        callback=jobs_callbacks.continue_schedule_callback,
        time=str_to_time(settings.schedule_extension_time),
        days=settings.schedule_extension_weekdays,
    )

    dispatcher.add_handler(registration_conv)

    return dispatcher
