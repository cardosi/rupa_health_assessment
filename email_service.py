import json
import os

import requests
from dotenv import load_dotenv

from email_types import (
    EmailAttemptData, EmailData, ResponseData, EmailProvider
)

load_dotenv()
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_API_URL = os.getenv('MAILGUN_API_URL')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_API_URL = os.getenv('SENDGRID_API_URL')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))


class EmailService:
    def __init__(
        self, service: EmailProvider = "MAILGUN",
        retry: bool = False, email_provider_fallback: bool = False
    ):
        self.service = service
        self.retry = retry
        self.email_provider_fallback = email_provider_fallback

    def send_email(self, data: EmailData) -> ResponseData:
        attempts = []
        if self.service == 'MAILGUN':
            response = self._send_with_retry(
                self.send_email_mailgun, data, attempts
            )
            if not response['send_success'] and self.email_provider_fallback:
                response = self._send_with_retry(
                    self.send_email_sendgrid, data, attempts
                )
        elif self.service == 'SENDGRID':
            response = self._send_with_retry(
                self.send_email_sendgrid, data, attempts
            )
            if not response['send_success'] and self.email_provider_fallback:
                response = self._send_with_retry(
                    self.send_email_mailgun, data, attempts
                )
        else:
            raise ValueError("Invalid service")
        return response

    def _send_with_retry(
            self,
            send_email_func,
            data: EmailData,
            attempts: list) -> ResponseData:
        for _ in range(MAX_RETRIES + 1):
            attempt = send_email_func(data)
            attempts.append(attempt)
            if not (400 <= attempt['status_code'] < 600) or not self.retry:
                break
        send_success = 200 <= attempts[-1]['status_code'] < 300
        return {
            'email_data': data,
            'attempts': attempts,
            'send_success': send_success,
            'final_attempt': attempts[-1]
        }

    def send_email_mailgun(self, data: EmailData) -> EmailAttemptData:
        response = requests.post(
            f"{MAILGUN_API_URL}/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"{data['from_name']} <{data['from_email']}>",
                "to": [f"{data['to_name']} <{data['to_email']}>"],
                "subject": data["subject"],
                "text": data["body"]
            }
        )
        return {
            'status_code': response.status_code,
            'service_name': 'MAILGUN',
            'response_body': response.text
        }

    def send_email_sendgrid(self, data: EmailData) -> EmailAttemptData:
        url = f"{SENDGRID_API_URL}/mail/send"
        post_data = {
            "personalizations": [{
                "to": [{
                    "email": data['to_email'],
                    "name": data['to_name']
                }],
                "subject": data["subject"]
            }],
            "content": [{
                "type": "text/plain",
                "value": data["body"]
            }],
            "from": {
                "email": data['from_email'],
                "name": data['from_name']
            },
            "reply_to": {
                "email": data['from_email'],
                "name": data['from_name']
            }
        }
        response = requests.request(
            "POST",
            url,
            data=json.dumps(post_data),
            headers={
                'authorization': f"Bearer {SENDGRID_API_KEY}",
                'content-type': "application/json"
            }
        )
        return {
            'status_code': response.status_code,
            'service_name': 'SENDGRID',
            'response_body': response.text
        }
