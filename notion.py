import datetime
import os

import notion_client

from helpers import Objectify, Expando


def create_client():
    notion_token = os.getenv('NOTION_TOKEN')

    client = notion_client.Client(auth=notion_token)

    return client


def get_user_data():
    client = create_client()

    notion_database_id = os.getenv('NOTION_DATABASE_ID')

    date = datetime.date.today().__str__()
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
