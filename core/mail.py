from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema

from core.config import email_conf


def send_email(
          background_tasks: BackgroundTasks,
          recipients: list,
          subject: str,
          template_body: dict
        ) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=template_body,
        subtype='html',
    )
    fm = FastMail(email_conf)

    background_tasks.add_task(
        fm.send_message,
        message, template_name='registration_confirmation.html',
    )
