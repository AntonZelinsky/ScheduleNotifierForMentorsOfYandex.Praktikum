import datetime
import os

from notion_client import APIResponseError, Client
from sqlalchemy.orm import Session

from core import models
from core.database import SessionLocal
from helpers import Expando, Objectify


def create_client():
    notion_token = os.getenv('NOTION_TOKEN')

    client = Client(auth=notion_token)

    return client


def get_database_ids() -> list:
    try:
        db: Session = SessionLocal()
        list_ids = [x.notion_db_id for x in db.query(models.Cohort.notion_db_id)]
    finally:
        db.close()
    return list_ids


def get_users_data() -> dict:
    raw_data = get_users_raw_data()
    users_data = group_by_user_raw_data(raw_data)
    return users_data


def get_users_raw_data() -> list:
    """Получить все дежурства во всех таблицах на сегодня."""
    client = create_client()
    date = datetime.date.today().__str__()
    users_raw_data = list()
    for notion_database_id in get_database_ids():
        try:
            response = client.databases.query(
                **{
                    "database_id": notion_database_id,
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
            # TODO назвать человечнее
            user_data.database_id = notion_database_id

            name = properties.Name.title
            if name:
                print(name[0].plain_text)
                user_data.name = name[0].plain_text

            email = properties.Email.rich_text
            if email:
                print(email[0].plain_text)
                user_data.email = email[0].plain_text

            telegram_id = properties.telegram_id.rich_text
            if telegram_id:
                print(telegram_id[0].plain_text)
                user_data.telegram_id = telegram_id[0].plain_text

            users_raw_data.append(user_data)

    return users_raw_data


def group_by_user_raw_data(raw_data: list) -> dict:
    """Сгруппировать всех дежурных по юзерам,
    т.к. один юзер может дежурить в нескольких когортах."""
    users_group_data = {}
    for user_data in raw_data:
        if user_data.email in users_group_data:
            users_group_data[user_data.email]['database_ids']\
                .append(user_data.database_id)
        else:
            user_dist_data = {
                user_data.email: {
                    'name': user_data.name,
                    'email': user_data.email,
                    'telegram_id': user_data.telegram_id,
                    'database_ids': [user_data.database_id]
                }
            }
            users_group_data.update(user_dist_data)
    return users_group_data
