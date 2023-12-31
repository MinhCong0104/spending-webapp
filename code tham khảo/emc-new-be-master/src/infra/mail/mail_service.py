import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import File, UploadFile
from typing import List
from src.infra.secret.secret_service import secret_service
from src.config.settings import settings


class MailService():

    async def get_mail_service_key(self):
        mail_secret = secret_service.get_secret(settings.mail_secret_name)
        return mail_secret.get('Key')

    async def send_mail(self, to: str, html: str, subject: str, attachments: List[UploadFile] = File(...)):
        api_key = await self.get_mail_service_key()
        sg = SendGridAPIClient(api_key)
        
        message = Mail(
            from_email=settings.support_email,
            to_emails=to,
            subject=subject,
            html_content=html,
            # attachments=attachments
        )
        response = sg.send(message)
        return response


mail_service = MailService()
