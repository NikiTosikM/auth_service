"""Тут будут хранится все задачки для celery"""

from src.core.celery.config import celery_app
from src.auth.service.business.email_manager import EmailService
from src.core.email.config import EmailConfig
from loguru import logger


@celery_app.task
def send_email_message_to_user(user_data: dict):
    logger.info("Отправка письма на почту и добавление его в 'Отправленные' ")
    with (
        EmailConfig.create_smtp_connection() as smtp,
        EmailConfig.create_imap_connection() as imap,
    ):
        service = EmailService(smtp_connect=smtp, imap_connect=imap)

        message = service.create_message(user_data)

        service.send_message(message)
        service.save_message(message)
