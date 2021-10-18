import datetime
import logging
import os

from queue import Queue
from threading import Thread

from pytz import timezone
from telegram import ParseMode, Bot
from telegram.ext import CommandHandler, Dispatcher
from telegram.ext import Updater, CallbackContext

import notion


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет, {update.effective_chat.full_name}, "
                                  "я буду присылать тебе уведомления о дежурстве в Я.П, "
                                  f"твой telegram id *{update.effective_chat.id}*.", parse_mode=ParseMode.MARKDOWN)
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')


def callback_morning_reminder(context: CallbackContext):
    user = notion.get_user_data()

    context.bot.send_message(chat_id=user.telegram_id,
                             text=f'Доброе утро, {user.name}. Напоминаю, ты сегодня дежуришь.\n\n'
                                  'Желаю хорошего дня!')
    logging.info(f'{user.name} c id {user.telegram_id} получил утреннее напоминание о дежурстве')


def callback_evening_reminder(context: CallbackContext):
    user = notion.get_user_data()

    context.bot.send_message(chat_id=user.telegram_id,
                             text=f'Добрый вечер, {user.name}. Ещё раз напоминаю, ты сегодня дежуришь.\n\n'
                                  'Спокойной ночи!')
    logging.info(f'{user.name} c id {user.telegram_id} получил вечернее напоминание о дежурстве')


def init():
    token = os.getenv('TELEGRAM_TOKEN')
    webhook_url = os.getenv('DOMAIN_ADDRESS')
    start_handler = CommandHandler('start', start)

    """Если webhook_url не задан -> запускаем приложение через пуллинг."""
    if webhook_url:
        bot = Bot(token)
        update_queue = Queue()

        dispatcher = Dispatcher(bot, update_queue)
        # dispatcher.add_handler(start)

        bot.set_webhook(webhook_url)
        thread = Thread(target=dispatcher.start, name='dispatcher')
        thread.start()
        logging.info(f'Приложение работает через вебхук {webhook_url}')

        return update_queue, dispatcher
    
    updater = Updater(token, use_context=True)

    # вынести логику ремайндеров в методы, оформить в качестве хэндлеров?
    morning_reminder_hour = int(os.getenv('MORNING_REMINDER_HOUR', int))
    time = datetime.time(hour=morning_reminder_hour, tzinfo=timezone("Europe/Warsaw"))
    updater.job_queue.run_daily(callback_morning_reminder, time)

    evening_reminder_hour = int(os.getenv('EVENING_REMINDER_HOUR', int))
    time = datetime.time(hour=evening_reminder_hour, tzinfo=timezone("Europe/Warsaw"))
    updater.job_queue.run_daily(callback_evening_reminder, time)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    updater.start_polling()

    logging.info('Приложение успешно запущено через пулинг')