import logging
from telegram import ParseMode, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ConversationHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from handlers.constants import CONFIRM_EMAIL, EMAIL


# временные переменные для хранения данных о пользователе
username = ''
emai_address = ''


def register_new_user(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, для получения уведомлений вам необходимо зарегестрироваться.\n"
        f"Пришлите мне ваше имя.", parse_mode=ParseMode.MARKDOWN)
    logging.info(
        f'Добавился пользователь с именем {update.effective_chat.full_name}, '
        f'юзернеймом {update.effective_chat.username} и id {update.effective_chat.id}')

    return EMAIL


def request_email(update, context):
    if update.callback_query:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Окей, давай изменим адрес электронной почты, "
                "на которую зарегестрирован твой аккаунт Notion."))
    else:
        username = update.message.text
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Отлично, {username}! Теперь пришли мне адрес электронной почты, "
                "на которую зарегестрирован твой аккаунт Notion."))
    return CONFIRM_EMAIL


def confirmation_sent(update, context):
    email_address = update.message.text
    buttons = [
        [InlineKeyboardButton(text='Отправить повторно', callback_data='resend_email')],
        [InlineKeyboardButton(text='Изменить почту', callback_data='change_email_address')]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"На твою почту {email_address} было отправлено письмо с подтверждением, "
            "следуй инструкциям в письме для завершения процесса регистрации"),
        reply_markup=keyboard)


def edit_details(update, context):
    answer = update.callback_query.data
    if answer == 'change_email_address':
        request_email(update, context)
    elif answer == 'resend_email':
        confirmation_sent(update, context)

registration_conv = ConversationHandler(
    entry_points=[
        CommandHandler('start', register_new_user)
    ],
    states={
        EMAIL: [
            MessageHandler(Filters.text, request_email)
        ],
        CONFIRM_EMAIL: [
            MessageHandler(Filters.text, confirmation_sent)
        ]
    },
    fallbacks=[CallbackQueryHandler(edit_details)]
)
