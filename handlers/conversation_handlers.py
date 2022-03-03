import logging

from telegram import ParseMode, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from core.models import User
from handlers import commands, states

from app.services import UserService
from fastapi import BackgroundTasks
from core.database import SessionLocal
user_service: UserService = UserService(BackgroundTasks(), SessionLocal())

# Variables for user data
EMAIL = "email"
USERNAME = "username"
TELEGRAM_ID = "user_telegram_id"


def validate_user_registration(update, context):
    """Validates user telegram id + confirmation code pair"""
    user = User.objects.filter(id=update.effective_chat.id)
    code = context.args[0]
    if user and code == user.uuid:
        # TODO: создаем запись в модели Registrations
        logging.info(f"Пользователь {user.name} успешно зарегистрирован")
        return states.MAIN
    logging.info(f"Не удалось подтвердить регистрацию пользователя {user.name} c кодом {code}")
    register_new_user(update, context)


def start(update, context):
    """Entry point for signup dialogue, checks if deeplink argument exists"""
    if context.args:
        validate_user_registration(update, context)
    return register_new_user(update, context)


def register_new_user(update, context):
    """Requests username and saves user's Telegram ID"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, для получения уведомлений тебе необходимо зарегистрироваться.\n"
             f"Пришли мне твоё имя или никнейм.",
        parse_mode=ParseMode.MARKDOWN,
    )
    logging.info(
        f"Добавился пользователь с именем {update.effective_chat.full_name}, "
        f"юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}"
    )
    context.user_data[TELEGRAM_ID] = update.effective_chat.id
    return states.REQUEST_EMAIL


def request_email(update, context):
    """Requests email and saves submitted username"""
    username = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Отлично, {username}! Теперь пришли мне адрес электронной почты, "
            "на которую зарегистрирован твой аккаунт Notion."
        ),
    )
    context.user_data[USERNAME] = username
    logging.info(f"Пользователь c ID {context.user_data[TELEGRAM_ID]} выбрал никнейм: {username}")
    return states.CONFIRM_EMAIL


def change_email(update, context):
    """Allows user to submit a different email address"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Хорошо, давай поменяем адрес электронной почты.\n"
            "Пришли адрес, который привязан к твоему аккаунту Notion."
        ),
    )
    logging.info(
        f"Пользователь {context.user_data[TELEGRAM_ID]} отправил запрос на смену почты"
    )
    return states.CONFIRM_EMAIL


def confirmation_sent(update, context):
    """
    Notifies the user that a confirmation email has been sent.
    Provides keyboard options for changing email address or resending the confirmation email.
    """
    if update.message:
        email_address = update.message.text
    else:
        email_address = context.user_data[EMAIL]
        # TODO: здесь будем создавать новую запись в таблице Registrations и отправлять письмо
    user_service.create_registration(dict(
        telegram_id=context.user_data[TELEGRAM_ID],
        name=update.effective_chat.full_name,
        email=email_address,
    ))
    buttons = [
        [InlineKeyboardButton(text="Отправить повторно", callback_data=commands.RESEND_CONF_LINK)],
        [InlineKeyboardButton(text="Изменить почту", callback_data=commands.UPDATE_EMAIL)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"На твою почту {email_address} было отправлено письмо с подтверждением, "
            "следуй инструкциям в письме для завершения процесса регистрации"
        ),
        reply_markup=keyboard,
    )
    context.user_data[EMAIL] = email_address
    logging.info(f"Отправили подтверждение пользователю ID {context.user_data[TELEGRAM_ID]} на почту {email_address}")
    return states.WAITING_CONFIRM


def main_func(update, context):
    # Здесь будет какой-то функционал для зарегистрированных пользователей
    pass


registration_conv = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
    ],
    states={
        states.REQUEST_EMAIL: [
            MessageHandler(Filters.text, request_email),
        ],
        states.CONFIRM_EMAIL: [
            MessageHandler(Filters.text, confirmation_sent),
        ],
        states.WAITING_CONFIRM: [
            CallbackQueryHandler(confirmation_sent, pattern=commands.RESEND_CONF_LINK),
            CallbackQueryHandler(change_email, pattern=commands.UPDATE_EMAIL),
        ],
        states.MAIN: [
            MessageHandler(Filters.text, main_func),
        ],
    },
    fallbacks=[]
)
