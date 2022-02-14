import logging

from fastapi import BackgroundTasks
from telegram.ext import CallbackContext

import notion
from app.services import CohortService
from core import config
from core.database import SessionLocal
from helpers import Objectify

settings = config.get_settings()
cohort_service: CohortService = CohortService(BackgroundTasks(), SessionLocal())


def morning_reminder_callback(context: CallbackContext):
    cohorts = cohort_service.get_cohorts()
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


def evening_reminder_callback(context: CallbackContext):
    cohorts = cohort_service.get_cohorts()
    users = notion.get_users_data(cohorts)

    for user_data in users.values():
        user = Objectify(user_data)
        if user.telegram_id:
            context.bot.send_message(chat_id=user.telegram_id,
                                     text=f'Добрый вечер, {user.name}. Ещё раз напоминаю, ты сегодня дежуришь.\n'
                                          f'В {" и ".join([cohort.name for cohort in user.databases])}\n\n'
                                          'Спокойной ночи!')
            logging.info(f'{user.name} c id {user.telegram_id} получил вечернее напоминание о дежурстве')


def continue_schedule_callback(context: CallbackContext):
    max_days = settings.schedule_extension_max_days
    cohorts = cohort_service.get_cohorts()
    for cohort in cohorts:
        added_duties = notion.add_duties_to_cohort(cohort, max_days=max_days)
        if added_duties:
            logging.info(f'В {cohort.name} продлено расписание.')
