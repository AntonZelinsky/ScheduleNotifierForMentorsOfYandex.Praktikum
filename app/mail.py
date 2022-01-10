from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from core.config import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_TLS=settings.mail_tls,
    MAIL_SSL=settings.mail_ssl,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs,
)


def send_email_in_bg(
          background_tasks: BackgroundTasks,
          recipients: list,
          subject: str,
          html: str,
        ) -> None:
    fm = FastMail(conf)

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html,
    )

    background_tasks.add_task(fm.send_message, message)
