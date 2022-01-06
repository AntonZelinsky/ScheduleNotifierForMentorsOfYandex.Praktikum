import logging
from telegram import ParseMode, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ConversationHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from handlers import states


# Variables for user data
EMAIL = "email"
USERNAME = "username"

# Constants for callback query data
UPDATE_EMAIL = "change_email_address"
RESEND_CONF_LINK = "resend_email"


def register_new_user(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, для получения уведомлений вам необходимо зарегестрироваться.\n"
        f"Пришлите мне ваше имя.",
        parse_mode=ParseMode.MARKDOWN,
    )
    logging.info(
        f"Добавился пользователь с именем {update.effective_chat.full_name}, "
        f"юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}"
    )
    return states.REQUEST_EMAIL


def request_email(update, context):
    username = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Отлично, {username}! Теперь пришли мне адрес электронной почты, "
            "на которую зарегестрирован твой аккаунт Notion."
        ),
    )
    context.user_data[USERNAME] = username
    logging.info(f"Пользователь выбрал никнейм: {username}")
    return states.CONFIRM_EMAIL


def change_email(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Хорошо, давай поменяем адрес электронной почты.\n"
            "Пришли адрес, который привязан к твоему аккаунту Notion."
        ),
    )
    logging.info(
        f"Пользователь {context.user_data[USERNAME]} отправил запрос на смену почты"
    )
    return states.CONFIRM_EMAIL


def confirmation_sent(update, context):
    if update.message:
        email_address = update.message.text
    else:
        email_address = context.user_data[EMAIL]
    buttons = [
        [
            InlineKeyboardButton(
                text="Отправить повторно", callback_data=RESEND_CONF_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить почту", callback_data=UPDATE_EMAIL
            )
        ],
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
    logging.info(f"Отправили подтверждение на почту {email_address}")
    return states.UPDATE_DATA


def check_user_data(update, context):
    action = update.callback_query.data
    if action == RESEND_CONF_LINK:
        return confirmation_sent(update, context)
    elif action == UPDATE_EMAIL:
        return change_email(update, context)


registration_conv = ConversationHandler(
    entry_points=[
        CommandHandler("start", register_new_user),
    ],
    states={
        states.REQUEST_EMAIL: [
            MessageHandler(Filters.text, request_email),
        ],
        states.CONFIRM_EMAIL: [
            MessageHandler(Filters.text, confirmation_sent),
        ],
        states.UPDATE_DATA: [
            CallbackQueryHandler(
                check_user_data, pass_user_data=True, pass_chat_data=True
            )
        ],
    },
    fallbacks=[]
)
