import datetime
import logging

from notion_client import APIResponseError, Client
from core.config import get_settings
from core.models import Cohort
from helpers import Expando, Objectify


def create_client():
    settings = get_settings()
    notion_token = settings.notion_token

    client = Client(auth=notion_token)

    return client


def get_mentors_on_duty(cohorts: list[Cohort]) -> dict:
    """Returns a dict of all on-duty mentors and their cohorts for today. Example: {mentor: [cohort1, cohort2]}"""
    client = create_client()
    date = datetime.date.today().__str__()
    mentors_on_duty = dict()
    for notion_database in cohorts:
        try:
            response = client.databases.query(
                **{
                    "database_id": notion_database.notion_db_id,
                    "filter": {
                        "property": "Дата",
                        "date": {
                            "equals": date,
                        },
                    },
                }
            )
            response = Objectify(response)
        except APIResponseError as e:
            raise ValueError(f'Notion fell: {e}')

        for item in response.results:
            properties = item.properties
            user_data = Expando()
            user_data.database = notion_database

            email = properties.Дежурный.people[0].person.email
            try:
                user_data.email = email
            except AttributeError:
                logging.error(f'Не найдено поле email среди данных, полученных из Notion.\n{properties}')

            if user_data.email in mentors_on_duty:
                mentors_on_duty[user_data.email].append(user_data.database)
            else:
                mentors_on_duty[user_data.email] = [user_data.database]

    return mentors_on_duty
