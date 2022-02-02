import logging
from queue import Queue
from threading import Thread

import telegram.ext
from pytz import timezone
from telegram import ParseMode, Bot
from telegram.ext import Updater, Dispatcher, JobQueue, Defaults

from bot import callbacks
from core import config
from handlers.conversation_handlers import registration_conv
from helpers import strptime

settings = config.get_settings()


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Привет, {update.effective_chat.full_name}, '
                                  'я буду присылать тебе уведомления о дежурстве в Я.П, '
                                  f'твой telegram id *{update.effective_chat.id}*.', parse_mode=ParseMode.MARKDOWN)
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')


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
    # Defining timezone of a bot for all datetime references (default is UTC)
    defaults = telegram.ext.Defaults(tzinfo=timezone('Europe/Moscow'))
    if settings.domain_address:
        webhook_url = f'{settings.domain_address}/{token}/telegramWebhook'
        dispatcher = init_webhook(token, webhook_url, defaults)
    else:
        dispatcher = init_polling(token, defaults)

    dispatcher.job_queue.run_daily(
        callback=callbacks.morning_reminder_callback,
        time=strptime(settings.morning_reminder_hour),
    )

    dispatcher.job_queue.run_daily(
        callback=callbacks.evening_reminder_callback,
        time=strptime(settings.evening_reminder_hour),
    )

    dispatcher.job_queue.run_daily(
        callback=callbacks.continue_schedule,
        time=strptime(settings.schedule_extension_time),
        days=settings.schedule_extension_weekdays,
    )

    dispatcher.add_handler(registration_conv)

    return dispatcher
