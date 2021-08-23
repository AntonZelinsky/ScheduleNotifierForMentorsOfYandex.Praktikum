import os

import notion_client
import datetime

from helpers import Objectify, Expando
NOTION_TOKEN = os.getenv('NOTION_TOKEN')

NOTION_DATABASE_NAME = os.getenv('NOTION_DATABASE_NAME')

notion = notion_client.Client(auth=NOTION_TOKEN)


def get_user_data():
    date = datetime.date.today().__str__()
    response = notion.databases.query(
        **{
            "database_id": NOTION_DATABASE_NAME,
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

        return user_data
