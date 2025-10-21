import time
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from imaplib import IMAP4, Time2Internaldate
from smtplib import SMTP

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from core.config import settings
from loguru import logger


@dataclass
class MessageSender:
    smtp_connect: SMTP

    def send_message(self, message: MIMEMultipart):
        self.smtp_connect.send_message(message)


@dataclass
class MessageSaver:
    imap_connect: IMAP4

    def add_message_to_sent_folder(self, message: MIMEMultipart):
        message_bytes = message.as_string().encode("utf-8")

        self.imap_connect.append(
            "Отправленные".encode("utf-8"),
            "\\Seen",
            Time2Internaldate(time.time()),
            message_bytes,
        )


class EmailService:
    """Работа с почтовым сервером"""

    env = Environment(
        loader=FileSystemLoader("static/templates/"),
        autoescape=select_autoescape(["html"]),
    )

    def __init__(self, smtp_connect: SMTP, imap_connect: IMAP4):
        self.sender = MessageSender(smtp_connect)
        self.saver = MessageSaver(imap_connect)

    @classmethod
    def create_message(cls, user_data: dict):
        msg = MIMEMultipart()

        # Add information for letters
        msg["Subject"] = "Рады видеть вас !"  # Заголовок сообщения
        msg["From"] = settings.email.sender_email  # Адрес отправителя
        msg["To"] = user_data["recipient_email"]  #  Адрес получателя

        # Generate HTML
        template: Template = cls.env.get_template("email_message.html")
        rendered_page: str = template.render(
            name=user_data["name"],
            last_name=user_data["last_name"],
            recipient_email=user_data["recipient_email"],
        )

        msg.attach(MIMEText(rendered_page, "html"))

        return msg

    def send_message(self, message, email_recipient):
        logger.debug(f"Отправка сообщения на адрес - {email_recipient}")
        self.sender.send_message(message=message)
        logger.debug(f"Выполнена отправка сообщения на адрес - {email_recipient}")

    def save_message(self, message):
        logger.debug("Добавление сообщения в  'Отправленные' ")
        self.saver.add_message_to_sent_folder(message=message)
        logger.debug("Сообщение добавленно в 'Отправленные' ")
