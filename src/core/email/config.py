from contextlib import contextmanager
from imaplib import IMAP4_SSL
from smtplib import SMTP_SSL, SMTPConnectError
from typing import Generator

from loguru import logger

from src.core.config import settings


class EmailConfig:
    sender_email: str = settings.email.sender_email
    sender_password: str = settings.email.sender_password

    smtp_hostname = "smtp.mail.ru"
    smtp_port = 465

    imap_hostname = "imap.mail.ru"
    imap_port = 993

    @classmethod
    @contextmanager
    def create_smtp_connection(cls) -> Generator[SMTP_SSL, None, None]:
        """Контекстный менеджер для SMTP соединения"""
        connection = None
        try:
            connection = SMTP_SSL(host=cls.smtp_hostname, port=cls.smtp_port)
            connection.login(user=cls.sender_email, password=cls.sender_password)

            logger.debug("Установлено SMTP соединение")

            yield connection
        except SMTPConnectError as conn_error:
            print(f"Ошибка при соединении с SMTP сервером: {conn_error}")
            raise
        except Exception as error:
            logger.error(f"Ошибка SMTP соединения: {error}")
            raise
        finally:
            if connection:
                connection.quit()

    @classmethod
    @contextmanager
    def create_imap_connection(cls) -> Generator[IMAP4_SSL, None, None]:
        """Контекстный менеджер для IMAP соединения"""
        connection = None
        try:
            connection = IMAP4_SSL(host=cls.imap_hostname, port=cls.imap_port)
            connection.login(user=cls.sender_email, password=cls.sender_password)

            logger.debug("Установлено IMAP соединение")

            yield connection
        except Exception as error:
            logger.error(f"Ошибка IMAP соединения: {error}")
            raise
        finally:
            if connection:
                connection.logout()
