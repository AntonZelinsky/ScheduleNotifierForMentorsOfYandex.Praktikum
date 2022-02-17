import datetime
import logging

from notion_client import APIResponseError, Client

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


class NotionServices(NotionClient):
    """
    Services class, contains all functionality for receiving and processing data from Notion API
    """
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

    def get_mentors_on_duty(self, cohorts: list[Cohort]) -> dict:
        """
        Returns a dict of all on-duty mentors and their cohorts for today.
        Example: {mentor@email.here: [cohort1, cohort2]}
        """
        mentors_on_duty = dict()
        for notion_database in cohorts:
            response = self.get_cohort_schedule_from_notion(notion_database)

            for item in response.results:
                properties = item.properties
                user_data = Expando()
                user_data.database = notion_database

                user_data.email = properties.Дежурный.people[0].person.email
                if user_data.email in mentors_on_duty:
                    mentors_on_duty[user_data.email].append(user_data.database)
                else:
                    mentors_on_duty[user_data.email] = [user_data.database]

        return mentors_on_duty
