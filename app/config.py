from pydantic import BaseSettings


DEBUG_MODE = True


class BaseConfig(BaseSettings):
    """
    Базовый класс и валидатор для всех переменных окружения.
    Значение, предоставленное в этом классе,
    будет использовано в случае если его нет в .env файле
    """
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


# TODO добавить необходимые перменные или методы для прода и тестов
class TestConfig(BaseConfig):
    sqlalchemy_database_url: str


class ProductionConfig(BaseConfig):
    pass


config = {
    'base': BaseConfig,
    'test': TestConfig,
    'production': ProductionConfig,
}
