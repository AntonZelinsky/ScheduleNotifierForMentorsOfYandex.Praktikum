from functools import lru_cache

from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    """
    Базовый класс и валидатор для всех переменных окружения.
    Значение, предоставленное в этом классе,
    будет использовано в случае если оно не задано в .env файле
    """
    debug: bool = True
    telegram_token: str
    notion_token: str
    notion_database_id: str
    morning_reminder_hour: int = 10
    evening_reminder_hour: int = 20
    domain_address: str = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


# TODO добавить необходимые перменные или методы для прода и тестов
class DevelopmentConfig(BaseConfig):
    sqlalchemy_database_url: str = 'postgresql://root:root@localhost:35432/schedule_notifier'


class TestConfig(BaseConfig):
    sqlalchemy_database_url: str = 'postgresql://root:root@localhost:35432/schedule_notifier'


class ProductionConfig(BaseConfig):
    debug: bool = False
    sqlalchemy_database_url: str


config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig,
}


@lru_cache()
def get_settings():
    if BaseConfig().debug:
        return config['development']()
    return config['production']()
