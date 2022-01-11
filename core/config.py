from functools import lru_cache

from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    """
    Базовый класс и валидатор для всех переменных окружения.
    Значение, предоставленное в этом классе,
    будет использовано в случае если оно не задано в .env файле
    """
    environment: str = 'development'
    debug: bool = True
    telegram_token: str
    notion_token: str
    morning_reminder_hour: int = 10
    evening_reminder_hour: int = 20
    domain_address: str = None
    port: int = 80
    sqlalchemy_database_url: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class DevelopmentConfig(BaseConfig):
    sqlalchemy_database_url: str = 'postgresql://root:root@localhost:35432/schedule_notifier'
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int = 587
    mail_server: str
    mail_from_name: str
    mail_tls: bool = False
    mail_ssl: bool = True
    use_credentials: bool = True
    validate_certs: bool = True
    template_folder: str = './app/templates'


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
