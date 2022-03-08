from functools import lru_cache

from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    """
    Базовый класс и валидатор для всех переменных окружения.
    Значение, предоставленное в этом классе,
    будет использовано в случае если оно не задано в .env файле
    """
    # Bot
    environment: str = 'development'
    debug: bool = True
    telegram_token: str
    notion_token: str
    morning_reminder_hour: str = '10:30'
    evening_reminder_hour: str = '20:15'
    domain_address: str = None
    port: int = 80

    # Postgres
    sqlalchemy_database_url: str
    schedule_extension_max_days: int = 14
    schedule_extension_time: str = '21:21'
    schedule_extension_weekdays: tuple = (6,)  # воскресенье
    timezone: str = 'Europe/Warsaw'
    db_user: str
    db_password: str
    db_name: str

    # Mail
    mail_username: str
    mail_password: str
    mail_port: int = 465
    mail_server: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class DevelopmentConfig(BaseConfig):
    sqlalchemy_database_url: str = 'postgresql://root:root@localhost:35432/schedule_notifier'


class ProductionConfig(BaseConfig):
    environment: str = 'production'
    debug: bool = False
    port: int = 80


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}


@lru_cache()
def get_settings():
    environment = BaseConfig().environment or 'development'
    settings = config.get(environment)
    if settings:
        return settings()
    raise EnvironmentError('Wrong environment')
