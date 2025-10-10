""" Тут будут хранится все задачки для celery """


from core.celery.config import celery_app
from auth.service.business.email_manager import EmailService
from core.email.config import EmailConfig


@celery_app.task
def send_email_message_to_user(user_data: dict):
    with EmailConfig.create_smtp_connection() as smtp, \
        EmailConfig.create_imap_connection() as imap:
        service =  EmailService(smtp_connect=smtp, imap_connect=imap)

        message = service.create_message(user_data)
        
        service.send_message(message)
        service.save_message(message)
    