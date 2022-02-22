import datetime
import logging

from notion_client import APIResponseError, Client

from core.config import get_settings
from core.models import Cohort
from helpers import Objectify


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
