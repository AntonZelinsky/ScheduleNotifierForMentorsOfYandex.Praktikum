from core.models import Cohort
from core.notion_integration import NotionClient
from helpers import Expando


class NotionServices:
    """
    Services class, contains all functionality for receiving and processing data from Notion API
    """
    def __init__(self):
        self.client = NotionClient()

    def get_mentors_on_duty(self, cohorts: list[Cohort]) -> dict:
        """
        Returns a dict of all on-duty mentors and their cohorts for today.
        Example: {mentor@email.here: [cohort1, cohort2]}
        """
        mentors_on_duty = dict()
        for notion_database in cohorts:
            response = self.client.get_cohort_schedule_from_notion(notion_database)

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
