import datetime

from dateutil.parser import parse
from fastapi import BackgroundTasks
from notion_client import APIResponseError, Client

from app.services import UserService
from core.config import get_settings
from core.database import SessionLocal
from core.models import Cohort
from helpers import Expando, Objectify

user_service: UserService = UserService(BackgroundTasks(), SessionLocal())


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
            'last_mentors_ids': tuple, крайние дежурства. **Порядок обратный --** от последнего к первому.
            'actual_date': date(%Y-%m-%d), крайняя заполненная дата (%Y-%m-%d)
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


def find_cycle_by_last_duties(last_duties: tuple) -> tuple:
    """
    Получить цикл дежурств наставнико из последовательности крайних дежурств.
    Подразумеваем, что цикл точно есть, минимум 1.
    Что последовательность из элементов по одному.
    Последовательность дана **в обратном порядке.**
    :return: tuple. Вернуть **в прямом порядке.**
    """
    cycle = []
    for i, mentor_id in enumerate(last_duties):
        # TODO: возможно ли одним запросом получить юзеров в список, и в цикле уже его использовать?
        user = user_service.get_user_by_notion_id(mentor_id)
        if user in cycle:
            break
        cycle.insert(i, user)
    return tuple(reversed(cycle))


def make_timeline(cycle: tuple, start_date: str, set_interval: int) -> list:
    """
    Сделать список-таймлайн. В списке на каждую дату назначен наставник.
    :param cycle: цикл дежурств,
    :param start_date: крайняя дата заполненного расписания,
    :param set_interval: кол-во дней добавляемых к расписанию,
    :return: Список расписание на :set_interval дней, от :start_date + 1. На каждую дату назначен наставник.
    """
    future_duties = [None] * set_interval
    duty_date = start_date
    for i, v in enumerate(future_duties):
        duty_date += datetime.timedelta(days=1)
        future_duties[i] = (dict(mentor=cycle[i % len(cycle)], date=duty_date))

    return future_duties


# TODO: Добавить обработку исключений
def add_duties_to_cohort(cohort: Cohort, set_interval: int = 7):
    """
    Генерировать расписание для когорты
    :param cohort: когорта
    :param set_interval: кол-во дней добавляемых к расписанию,
    :return: список добавленных ноушен страниц
    """
    client = create_client()

    last_duties = get_last_duties_by_cohort(cohort)
    cycle = find_cycle_by_last_duties(last_duties['last_mentors_ids'])
    timeline = make_timeline(cycle, last_duties['actual_date'], set_interval)

    added = []
    for duty in timeline:
        # TODO: возможно ли одним запросом добавить все необходимые страницы?
        response = client.pages.create(
            **{
                "parent": {
                    "database_id": str(cohort.notion_db_id)
                },
                "properties": {
                    "Дата": {
                        "date": {
                            "start": duty['date'].isoformat(),
                            "end": None
                        }
                    },
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": duty['mentor'].name
                                }
                            }
                        ]
                    },
                    "Дежурный": {
                        "people": [
                            {
                                "object": "user",
                                "id": str(duty['mentor'].notion_user_id)
                            }
                        ]
                    }
                }
            }
        )
        added.append(response['id'])
    return added
