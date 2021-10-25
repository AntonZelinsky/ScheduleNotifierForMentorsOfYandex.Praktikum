from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    telegram_token: str
    notion_token: str
    notion_database_id: str
    morning_reminder_hour: int = 10
    evening_reminder_hour: int = 20
    domain_address: str
    port: int = 80

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class TestConfig(BaseConfig):
    debug: str = None


class ProductionConfig(BaseConfig):
    pass
