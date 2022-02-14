import datetime
import logging

from dateutil.parser import parse
from fastapi import BackgroundTasks
from notion_client import APIResponseError, Client

from app.schemas import DutyPageCreate
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
            responseus = client.databases.query(
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
            response = Objectify(responseus)
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
    date_now = datetime.date.today().__str__()
    databases_duties = query_databases_duties(
        database_id=cohort.notion_db_id,
        date=date_now,
        page_size=count_days,
    )

    if len(databases_duties) < 2:
        logging.error('Недостаточно данных для расчета расписания. Нужен минимум один цикл дежурств в будущем.')
        return False
    last_duties = [duty.properties for duty in databases_duties]
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
    Получить цикл дежурств наставников из последовательности крайних дежурств.
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


def make_timeline(cycle: tuple, start_date: str, set_period: int) -> list:
    """
    Сделать список-таймлайн. В списке на каждую дату назначен наставник.
    :param cycle: цикл дежурств,
    :param start_date: крайняя дата заполненного расписания,
    :param set_period: кол-во дней добавляемых к расписанию,
    :return: Список расписание на :set_interval дней, от :start_date + 1. На каждую дату назначен наставник.
    """
    future_duties = [None] * set_period
    duty_date = start_date
    for i, v in enumerate(future_duties):
        duty_date += datetime.timedelta(days=1)
        future_duties[i] = (dict(mentor=cycle[i % len(cycle)], date=duty_date))

    return future_duties


# TODO: Добавить обработку исключений
def add_duties_to_cohort(cohort: Cohort, max_days: int = 14):
    """
    Генерировать расписание для когорты
    :param cohort: когорта
    :param max_days: кол-во дней добавляемых к расписанию,
    :return: список добавленных ноушен страниц
    """

    last_duties = get_last_duties_by_cohort(cohort)
    if not last_duties:
        return False

    need_days = datetime.date.today() + datetime.timedelta(days=max_days) - last_duties['actual_date']
    need_days = need_days.days
    if need_days < 1:
        logging.info(f'Когорта "{cohort.name}" не нуждается в продлении расписания. '
                     f'Похоже, оно уже заполнено как минимум на {max_days} дней вперед.')
        return False

    cycle = find_cycle_by_last_duties(last_duties['last_mentors_ids'])
    timeline = make_timeline(cycle, last_duties['actual_date'], need_days)

    added = []
    for duty in timeline:
        added_page_id = create_duty_page(DutyPageCreate(
            database_id=cohort.notion_db_id,
            date=duty['date'].isoformat(),
            mentor_name=duty['mentor'].name,
            notion_user_id=duty['mentor'].notion_user_id,
        ))
        added.append(added_page_id)
    return added


def create_duty_page(duty_page: DutyPageCreate) -> int:
    client = create_client()

    response = client.pages.create(
        **{
            "parent": {
                "database_id": str(duty_page.database_id)
            },
            "properties": {
                "Дата": {
                    "date": {
                        "start": str(duty_page.date),
                        "end": None
                    }
                },
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": duty_page.mentor_name
                            }
                        }
                    ]
                },
                "Дежурный": {
                    "people": [
                        {
                            "object": "user",
                            "id": str(duty_page.notion_user_id)
                        }
                    ]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "text": [{
                            "type": "text",
                            "text": {
                                "content": "Автосгенерированное"
                            }
                        }],
                        "icon": {
                            "emoji": "🤖"
                        }
                    }
                }
            ]
        }
    )
    return response['id']


def query_databases_duties(database_id: str, date: str, page_size: int) -> list:
    client = create_client()

    response = client.databases.query(
        **{
            "database_id": database_id,
            "filter": {
                "property": "Дата",
                "date": {
                    "on_or_after": date
                }
            },
            "sorts": [{
                "property": "Дата",
                "timestamp": "created_time",
                "direction": "descending"
            }],
            "page_size": page_size
        }
    )
    response = Objectify(response)
    return response.results
