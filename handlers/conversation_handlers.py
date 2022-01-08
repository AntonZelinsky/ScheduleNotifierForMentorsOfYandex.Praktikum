import logging
from telegram import ParseMode, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ConversationHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from handlers import commands, states

# Variables for user data
EMAIL = "email"
USERNAME = "username"
TELEGRAM_ID = "user_telegram_id"


def register_new_user(update, context):
    if context.args:
        # TODO: сделать сверку кода из диплинка с кодом из БД
        # если код подтверждения не валиден - запустить процесс регистрации заново
        print("Deeplink found!")
        confirmation_code = context.args[0]
        logging.info(f"Код подтверждения: {confirmation_code}")
        return registration_confirmed(update, context)
    else:
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
        context.user_data[TELEGRAM_ID] = update.effective_chat.id
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
    logging.info(f"Пользователь c ID {context.user_data[TELEGRAM_ID]} выбрал никнейм: {username}")
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
        f"Пользователь {context.user_data[TELEGRAM_ID]} отправил запрос на смену почты"
    )
    return states.CONFIRM_EMAIL


def confirmation_sent(update, context):
    if update.message:
        email_address = update.message.text
    else:
        email_address = context.user_data[EMAIL]
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
    # Здесь должен активироваться метод отправки письма и генериться уникальный код подтверждения
    logging.info(f"Отправили подтверждение пользователю ID {context.user_data[TELEGRAM_ID]} на почту {email_address}")
    return states.WAITING_CONFIRM


def registration_confirmed(update, context):
    # TODO: почта успешно подтверждена -> создаем запись с новым подтвержденным пользователем в БД
    context.bot.send_message(chat_id=update.effective_chat.id, text="Регистрация успешно завершена")


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
        states.WAITING_CONFIRM: [
            CallbackQueryHandler(confirmation_sent, pattern=commands.RESEND_CONF_LINK),
            CallbackQueryHandler(change_email, pattern=commands.UPDATE_EMAIL),
        ],
    },
    fallbacks=[]
)
