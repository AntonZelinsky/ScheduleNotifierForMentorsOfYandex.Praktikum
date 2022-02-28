import datetime
import logging

from notion_client import APIResponseError, Client

from app.schemas import DutyPageCreate
from core.config import get_settings
from core.models import Cohort
from helpers import Expando, Objectify


class NotionClient:
    """
    Base class for a Notion Client instance.
    Creates a client for a Notion integration that was provided in the config file.
    """
    notion_token = get_settings().notion_token

    def __init__(self):
        self.client = Client(auth=self.notion_token)

    def get_cohort_schedule_from_notion(self, cohort: Cohort):
        """Gets the latest schedule for a cohort from Notion API"""
        date = datetime.date.today().__str__()
        try:
            response = self.client.databases.query(
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

    def get_users_raw_data(self, cohorts: list[Cohort]) -> list:
        """Получить все дежурства во всех таблицах на сегодня."""
        date = datetime.date.today().__str__()
        users_raw_data = list()
        for notion_database in cohorts:
            try:
                response = self.client.databases.query(
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

                name = properties.Name.title
                if name:
                    print(name[0].plain_text)
                    user_data.name = name[0].plain_text

                telegram_id = properties.telegram_id.rich_text
                if telegram_id:
                    print(telegram_id[0].plain_text)
                    user_data.telegram_id = telegram_id[0].plain_text

                users_raw_data.append(user_data)

        return users_raw_data

    def create_duty_page(self, duty_page: DutyPageCreate) -> int:
        response = self.client.pages.create(
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

    def query_databases_duties(self, database_id: str, date: str, page_size: int) -> list:
        response = self.client.databases.query(
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
