import datetime
import os
from typing import List

from notion_client import APIResponseError, Client

from app import schemas, services
from helpers import Expando, Objectify


def create_client():
    notion_token = os.getenv('NOTION_TOKEN')

    client = Client(auth=notion_token)

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
    # TODO добавить обаботку пагинации. Сейчас можем получить максимум 100.
    """Получить все Databases в которых встреачается
    вхождение название когорты.
    Пустая строка -- все Databases"""
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
    except APIResponseError as e:
        raise ValueError(f'Notion fell: {e}')
    return response


def sync_notion_databases_to_db(session) -> List:
    """Синхронизировать все Databases из Ноушена в БД.
    Вернуть добавленные Databases."""
    created_databases = []
    all_databases = query_databases_by_str("")
    for db in all_databases:
        name = db['title'][0]['text']['content']
        notion_db_id = db['id']
        cohort = schemas.CohortCreate(name=name, notion_db_id=notion_db_id)
        try:
            added_cohort = services.create_cohort(session, cohort)
            # Объекты модели некорректно складываются в список, а пидантик норм
            added_cohort = schemas.Cohort.from_orm(added_cohort)
            created_databases.append(added_cohort)
        except ValueError:
            pass
    return created_databases
