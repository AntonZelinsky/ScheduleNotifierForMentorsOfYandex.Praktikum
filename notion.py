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


def get_users_data(cohorts: list[Cohort]) -> dict:
    raw_data = get_users_raw_data(cohorts)
    users_data = group_by_user_raw_data(raw_data)
    return users_data


def get_users_raw_data(cohorts: list[Cohort]) -> list:
    """Получить все дежурства во всех таблицах на сегодня."""
    client = create_client()
    date = datetime.date.today().__str__()
    users_raw_data = list()
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

            users_raw_data.append(user_data)

    return users_raw_data


def group_by_user_raw_data(raw_data: list) -> dict:
    """Сгруппировать всех дежурных по юзерам,
    т.к. один юзер может дежурить в нескольких когортах."""
    users_group_data = {}
    for user_data in raw_data:
        if user_data.email in users_group_data:
            users_group_data[user_data.email] \
                .append(user_data.database)
        else:
            user_dist_data = {
                user_data.email: [user_data.database],
            }
            users_group_data.update(user_dist_data)
    return users_group_data
