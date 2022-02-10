import datetime
import logging

from notion_client import APIResponseError, Client

from app.exceptions import EmailNotFoundError
from core.config import get_settings
from core.models import Cohort
from helpers import Expando, Objectify


def create_client():
    settings = get_settings()
    notion_token = settings.notion_token

    client = Client(auth=notion_token)

    return client


def get_cohort_schedule_from_notion(cohort: Cohort):
    """Gets the latest schedule for a cohort from Notion API"""
    client = create_client()
    date = datetime.date.today().__str__()
    try:
        response = client.databases.query(
            **{
                "database_id": cohort.notion_db_id,
                "filter": {
                    "property": "Дата",
                    "date": {
                        "equals": date,
                    },
                },
            }
        )
        response = Objectify(response)
        return response
    except APIResponseError as e:
        logging.error(f'Не удалось получить ответ от API для когорты:\n{cohort}\nДата: {date}\n'
                      f'APIResponseError: {e}')
        raise ValueError(f'Ошибка при попытке обращения к Notion API: {e}')


def get_mentors_on_duty(cohorts: list[Cohort]) -> dict:
    """
    Returns a dict of all on-duty mentors and their cohorts for today.
    Example: {mentor@email.here: [cohort1, cohort2]}
    """
    mentors_on_duty = dict()
    for notion_database in cohorts:
        response = get_cohort_schedule_from_notion(notion_database)

        for item in response.results:
            properties = item.properties
            user_data = Expando()
            user_data.database = notion_database

            email = properties.Дежурный.people[0].person.email
            try:
                user_data.email = email
            except Exception as e:
                logging.error(f'Не удалось найти email в ответе от API: {properties.Дежурный.people[0]}')
                print(e)
                raise EmailNotFoundError('Поле email - обязательное!')

            if user_data.email in mentors_on_duty:
                mentors_on_duty[user_data.email].append(user_data.database)
            else:
                mentors_on_duty[user_data.email] = [user_data.database]

    return mentors_on_duty
