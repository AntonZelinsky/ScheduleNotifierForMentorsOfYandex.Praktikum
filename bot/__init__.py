import datetime
import logging
from queue import Queue
from threading import Thread

import notion
from helpers import Objectify
from pytz import timezone
from telegram import Bot, ParseMode, ReplyKeyboardMarkup
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Dispatcher, Filters, JobQueue, MessageHandler,
                          Updater)

from core.config import get_settings

settings = get_settings()

# вынести в отдельный файл с константами
NAME, EMAIL = range(2)
REPLY_KEYBOARD = [['Отправить письмо повторно', 'Изменить адрес почты']]


def start_test(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет, {update.effective_chat.full_name}, "
                                  "я буду присылать тебе уведомления о дежурстве в Я.П, "
                                  f"твой telegram id *{update.effective_chat.id}*.", parse_mode=ParseMode.MARKDOWN)
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')


def start(update, context):
    """ Начало диалога с новым пользователем """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет! Для того, чтобы начать получать уведомления о дежурстве"
                             " тебе необходимо зарегистрироваться.\n\nКак тебя зовут?")
    logging.info(f'Добавился пользователь с именем {update.effective_chat.full_name}, '
                 f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')
    return NAME


def request_email(update, context):
    """ Запрашиваем имейл, к которому привязан аккаунт ноушена """
    answer = update.message.text
    if answer == REPLY_KEYBOARD[0][1]:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Окей, давай изменим твою почту.\n👇')
        logging.info(f'Пришел запрос на изменение почты')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Отлично!\n{answer}, для завершения регистрации'
                                 ' пришли мне e-mail, к которому привязан твой аккаунт Notion.\n👇')
        logging.info(f'У нас новый пользователь: {answer}')

    return EMAIL


def verify_email(update, context):
    """
    Отправляем письмо на почту для завершения регистрации.
    Даем пользователю возможность изменить адрес или отправить подтверждение еще раз
    """
    email = update.message.text
    if email == REPLY_KEYBOARD[0][0]:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Отправили подтверждение еще раз.')
        logging.info('Получен запрос на повторную отправку подтверждения')
    elif email == REPLY_KEYBOARD[0][1]:
        logging.info('Получен запрос на повторную отправку подтверждения')
        request_email(update=update, context=context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Супер, мы отправили письмо с подтверждением на почту {email}.'
                                 '\nСледуй инструкциям в письме чтобы завершить процесс регистрации!',
                                 reply_markup=ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True))
        logging.info(f'Добавлен новый email: {email}')


def stop(update, context):
    """ Завершаем диалог """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Увидимся!')


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
    # webhook_url = f'{settings.domain_address}/{token}/telegramWebhook'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text, request_email)],
            EMAIL: [MessageHandler(Filters.text, verify_email)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    if settings.domain_address:
        webhook_url = f'{settings.domain_address}/{token}/telegramWebhook'
        dispatcher = init_webhook(token, webhook_url)
    else:
        dispatcher = init_pooling(token)

    time = datetime.time(hour=settings.morning_reminder_hour, tzinfo=timezone("Europe/Warsaw"))
    dispatcher.job_queue.run_daily(callback_morning_reminder, time)

    time = datetime.time(hour=settings.evening_reminder_hour, tzinfo=timezone("Europe/Warsaw"))
    dispatcher.job_queue.run_daily(callback_evening_reminder, time)

    dispatcher.add_handler(conv_handler)

    return dispatcher
