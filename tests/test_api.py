import unittest
from unittest.mock import patch
from flask import json
from app import app


class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.EmailService')
    def test_send_email(self, mock_email_service):
        # Define your test data
        data = {
            'from_name': 'Sender',
            'from': 'sender@example.com',
            'to_name': 'Recipient',
            'to': 'recipient@example.com',
            'subject': 'Test Email',
            'body': 'This is a test email.'
        }

        # Mock the send_email method of EmailService
        mock_email_service.return_value.send_email.return_value = {
            'email_data': data,
            'attempts': [{
                'status_code': 200,
                'service_name': 'MAILGUN',
                'response_body': 'Email sent successfully'
            }],
            'send_success': True,
            'final_attempt': {
                'status_code': 200,
                'service_name': 'MAILGUN',
                'response_body': 'Email sent successfully'
            }
        }

        response = self.app.post(
            '/email',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Test with invalid email provider
        response = self.app.post(
            '/email?emailProvider=INVALID',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        # Test with retry
        response = self.app.post(
            '/email?retry=true',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Test with email provider fallback
        response = self.app.post(
            '/email?emailProviderFallback=true',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Test when EmailService fails
        mock_email_service.return_value.send_email.return_value = {
            'email_data': data,
            'attempts': [{
                'status_code': 500,
                'service_name': 'MAILGUN',
                'response_body': 'Internal Server Error'
            }],
            'send_success': False,
            'final_attempt': {
                'status_code': 500,
                'service_name': 'MAILGUN',
                'response_body': 'Internal Server Error'
            }
        }

        response = self.app.post(
            '/email',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
