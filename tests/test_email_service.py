import os
import unittest
from unittest.mock import patch, MagicMock
from email_types import EmailData
from email_service import EmailService

MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))


class TestEmailService(unittest.TestCase):
    def setUp(self):
        self.email_data = EmailData(
            to_email="test@example.com",
            to_name="Test User",
            from_email="sender@example.com",
            from_name="Sender User",
            subject="Test Subject",
            body="Hello, World!"
        )

    @patch('requests.post')
    def test_send_email_mailgun(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = EmailService(service='MAILGUN')
        response = service.send_email_mailgun(self.email_data)

        self.assertEqual(response['status_code'], 200)
        self.assertEqual(response['service_name'], 'MAILGUN')

    @patch('requests.request')
    def test_send_email_sendgrid(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        service = EmailService(service='SENDGRID')
        response = service.send_email_sendgrid(self.email_data)

        self.assertEqual(response['status_code'], 200)
        self.assertEqual(response['service_name'], 'SENDGRID')

    @patch('requests.post')
    def test_retry_on_failure_mailgun(self, mock_post):
        mock_responses = [
            MagicMock(status_code=500), MagicMock(status_code=200)]
        mock_post.side_effect = mock_responses

        service = EmailService(service='MAILGUN', retry=True)
        response = service.send_email(self.email_data)

        self.assertEqual(response['send_success'], True)
        self.assertEqual(len(response['attempts']), 2)

    @patch('requests.request')
    def test_retry_on_failure_sendgrid(self, mock_request):
        mock_responses = [
            MagicMock(status_code=500), MagicMock(status_code=200)]
        mock_request.side_effect = mock_responses

        service = EmailService(service='SENDGRID', retry=True)
        response = service.send_email(self.email_data)

        self.assertEqual(response['send_success'], True)
        self.assertEqual(len(response['attempts']), 2)

    @patch('requests.post')
    @patch('requests.request')
    def test_provider_fallback_on_failure(self, mock_request, mock_post):
        mock_responses_mailgun = [
            MagicMock(status_code=500) for _ in range(MAX_RETRIES + 1)]
        mock_responses_sendgrid = [MagicMock(status_code=200)]
        mock_post.side_effect = mock_responses_mailgun
        mock_request.side_effect = mock_responses_sendgrid

        service = EmailService(
            service='MAILGUN',
            retry=True,
            email_provider_fallback=True)
        response = service.send_email(self.email_data)

        self.assertEqual(response['send_success'], True)
        self.assertEqual(len(response['attempts']), MAX_RETRIES + 2)


if __name__ == '__main__':
    unittest.main()
