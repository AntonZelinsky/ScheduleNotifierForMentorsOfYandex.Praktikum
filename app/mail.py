from fastapi_mail import ConnectionConfig, FastMail, MessageSchema


def send_email(recipients: list, subject: str, html: str) -> None:
    conf = ConnectionConfig(
        MAIL_USERNAME='YourUsername',
        MAIL_PASSWORD='strong_password',
        MAIL_FROM='your@email.com',
        MAIL_PORT=587,
        MAIL_SERVER='your mail server',
        MAIL_FROM_NAME='Desired Name',
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    fm = FastMail(conf)

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html,
        subtype='html',
    )
    fm.send_message(message)
