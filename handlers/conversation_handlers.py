import logging

from telegram import ParseMode, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from handlers import commands, states

# Variables for user data
EMAIL = "email"
USERNAME = "username"
TELEGRAM_ID = "user_telegram_id"


def start(update, context):
    """Entry point for signup dialogue, checks if deeplink argument exists"""
    user_id = update.effective_chat.id
    if context.args:
        print("Deeplink found!")
        confirmation_code = context.args[0]
        # псевдокод сверки:
        # user = User.objects.filter(id=user_id)
        # if user and confirmation_code == user.uuid -> успех, создаем запись в БД
        # else (если код подтверждения неверный) -> запускаем процесс регистрации заново
        logging.info(f"Сверяем код подтверждения {confirmation_code} с кодом пользователя {user_id}")
        context.bot.send_message(chat_id=user_id, text="Регистрация успешно завершена")
        return states.MAIN
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
