import logging
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema

from core.config import get_settings

settings = get_settings()


def send_email(
          background_tasks: BackgroundTasks,
          recipients: list,
          subject: str,
          template_body: dict,
          template_html,
        ) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=template_body,
        subtype='html',
    )
    logging.info(f"Отправляем. recipients:{recipients}, subject:{subject}, template_body:{template_body}")
    fm = FastMail(settings.email_conf())

    background_tasks.add_task(
        fm.send_message,
        message, template_name=template_html,
    )
