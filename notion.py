import datetime
import os
from uuid import UUID

import notion_client
from fastapi import HTTPException

from app import schemas
from helpers import Expando, Objectify


def create_client():
    notion_token = os.getenv('NOTION_TOKEN')

    client = notion_client.Client(auth=notion_token)

    return client


def get_database_ids() -> list:
    return os.getenv('NOTION_DATABASE_ID').split(',')


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


def query_databases_by_str(query: str):
    """Получить все Databases в которых встреачается
    вхождение название когорты"""
    client = create_client()
    try:
        response = client.search(
            **{
                "query": query,
                "filter": {
                    "value": "database",
                    "property": "object"
                }
            }
        ).get('results')
    except Exception as e:
        raise ValueError(f'Notion fell: {e}')
    return response


def is_databases_by_cohort_name(name: str) -> UUID or False:
    """Получить Databases UUID
    по точному совпадению заголовка с название когорты."""
    databases = query_databases_by_str(query=name)
    for db in databases:
        if db['title'][0]['text']['content'] == name:
            return db['id']
    return False


def create_calendar_database(cohort: schemas.Cohort):
    """Создать Database когорты на странице NOTION_PAGE_ID."""
    client = create_client()
    page_id = os.getenv('NOTION_PAGE_ID')
    db_uuid = is_databases_by_cohort_name(name=cohort.name)
    if db_uuid:
        raise HTTPException(
                status_code=400,
                detail=f'Notions database «{cohort.name}» {db_uuid} '
                       f'already added',
            )
    try:
        response = client.databases.create(
            **{
                "parent": {"page_id": page_id},
                "title": [{"text": {"content": cohort.name}}],
                "properties": {
                    "Name": {"title": {}},
                    "Дежурный": {"people": {}},
                    "Дата": {"date": {}}
                }
            }
        )
    except Exception as e:
        raise ValueError(f'Not created DB in Notions: {e}')
    response = Objectify(response)
    return response
