import datetime
from dateutil.parser import parse

from notion_client import APIResponseError, Client
from core import models
from core.config import get_settings
from core.database import SessionLocal
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
            # TODO назвать человечнее
            user_data.database = notion_database

            name = properties.Name.title
            if name:
                print(name[0].plain_text)
                user_data.name = name[0].plain_text

            # email = properties.Email.rich_text
            # if email:
            #     print(email[0].plain_text)
            #     user_data.email = email[0].plain_text

            telegram_id = properties.telegram_id.rich_text
            if telegram_id:
                print(telegram_id[0].plain_text)
                user_data.telegram_id = telegram_id[0].plain_text

            users_raw_data.append(user_data)

    return users_raw_data


def group_by_user_raw_data(raw_data: list) -> dict:
    """
    Сгруппировать всех дежурных по юзерам,
    т.к. один юзер может дежурить в нескольких когортах.
    """
    users_group_data = {}
    for user_data in raw_data:
        if user_data.email in users_group_data:
            users_group_data[user_data.email]['databases'] \
                .append(user_data.database)
        else:
            user_dist_data = {
                user_data.email: {
                    'name': user_data.name,
                    'email': user_data.email,
                    'telegram_id': user_data.telegram_id,
                    'databases': [user_data.database]
                }
            }
            users_group_data.update(user_dist_data)
    return users_group_data


def get_last_duties_by_cohort(cohort: Cohort, count_days: int = 7) -> dict:
    """
    Получить последовательность из `:count` крайних дежурств в обратном порядке.
    Данные из прошлого не учитываем.
    :param cohort: когорта,
    :param count_days: количество дней для расчета,
    :return:
        {
            'last_mentors_ids': tuple, крайние дежурства
            'actual_date': date(%Y-%m-%d), крайняя заполненая дата (%Y-%m-%d)
        }
    """
    client = create_client()
    date_now = datetime.date.today().__str__()
    response = client.databases.query(
        **{
            "database_id": cohort.notion_db_id,
            "filter": {
                "property": "Дата",
                "date": {
                    "on_or_after": date_now
                }
            },
            "sorts": [{
                "property": "Дата",
                "timestamp": "created_time",
                "direction": "descending"
            }],
            "page_size": count_days
        }
    )
    response = Objectify(response)

    last_duties = [duty.properties for duty in response.results]
    last_duties = sorted(last_duties, key=lambda duty: duty.Дата.date.start, reverse=True)
    actual_date = parse(last_duties[0].Дата.date.start).date()
    last_mentors_ids = tuple(duty.Дежурный.people[0].id for duty in last_duties)
    last_mentors = {
        "last_mentors_ids": last_mentors_ids,
        "actual_date": actual_date
    }

    return last_mentors


def calculate_cycle_by_last_duties(last_duties: tuple) -> tuple:
    """
    Получить цикл из последовательности.
    Подразумеваем, что цикл точно есть, минимум 1.
    Что последовательность из элементов по одному.
    Движение от 0-го элемента к последнему.
    :return: tuple
    """
    cycle = set()
    for mentor in last_duties:
        if mentor not in cycle:
            cycle.add(mentor)
        else:
            break
    return tuple(cycle)


def add_duties_to_cohort(cohort: Cohort, cycle: tuple, start_date: str, set_interval: int = 7):
    client = create_client()
    future_duties = [None] * set_interval
    duty_date = start_date
    for i, mentor in enumerate(future_duties):
        duty_date += datetime.timedelta(days=1)
        future_duties[i] = (dict(mentor=cycle[i % len(cycle)], date=duty_date))

    return future_duties
    # response = client.pages.create(
    #     **{
    #         "parent": {
    #             "database_id": str(cohort.notion_db_id)
    #         },
    #         "properties": {
    #             "Дата": {
    #                 "date": {
    #                     "start": "2022-02-13",
    #                     "end": None
    #                 }
    #             },
    #             "Name": {
    #                 "title": [
    #                     {
    #                         "text": {
    #                             "content": "Александр"
    #                         }
    #                     }
    #                 ]
    #             },
    #             "Дежурный": {
    #                 "people": [
    #                     {
    #                         "object": "user",
    #                         "id": "134d1a34-7876-4cb5-8493-2875f6751a86"
    #                     }
    #                 ]
    #             }
    #         }
    #     }
    # )
    # return future_duties
