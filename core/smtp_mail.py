import logging
import smtplib
from email.message import EmailMessage

from core.config import get_settings


settings = get_settings()


def send_email_confirmation(email_address: str) -> None:
    msg = EmailMessage()
    msg['Subject'] = 'Подтверждение регистрации | Бот для наставников Практикума'
    msg['From'] = settings.mail_username
    msg['To'] = email_address
    # TODO: сделать ф
    msg.set_content('''
    <!DOCTYPE html>
    <html>
        <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
        <div style="width: 100%; background: #F0F1F3; border-radius: 10px; padding: 10px;">
          <div style="margin: 0 auto; max-width: 600px; text-align: center;">
            <h3>Привет!</h3>
            <p>
              Для подтверждения регистрации в боте напоминаний о дежурствах в Яндекс.Практикуме
              <a href="{{ link }}" target="_blank">перейди в бот по ссылке</a>.
            </p>
          </div>
        </div>
        </body>
    </html>
    ''', subtype='html')

    with smtplib.SMTP_SSL(settings.mail_server, settings.mail_port) as smtp:
        smtp.login(settings.mail_username, settings.mail_password)
        smtp.send_message(msg)
        logging.info(f'Ссылка на подтверждение регистрации отправлена на почту {email_address}')
