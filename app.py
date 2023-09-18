import logging
import os
from flask import Flask, request, jsonify
from email_service import EmailService
from utils import validate_data, transform_data

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

EmailProviderList = ['MAILGUN', 'SENDGRID']


@app.route('/email', methods=['POST'])
def send_email():
    # Check if 'emailProvider' query parameter is included
    # and its value is of type EmailProvider
    provider = request.args.get(
        'emailProvider',
        default=os.getenv('DEFAULT_EMAIL_PROVIDER', 'MAILGUN')
    ).upper()
    if provider not in EmailProviderList:
        logging.error('Invalid email provider.')
        return jsonify({'message': 'Invalid email provider'}), 400

    retry = request.args.get('retry', default='false').lower() == 'true'
    email_provider_fallback = request.args.get(
        'emailProviderFallback',
        default='false'
    ).lower() == 'true'

    email_service = EmailService(provider, retry, email_provider_fallback)
    data = request.get_json()

    # Validate the input
    validate_data(data)

    data = transform_data(data)

    # Choose the email service provider and send the email
    response = email_service.send_email(data)

    # Check the status code of the final attempt
    final_attempt = response['final_attempt']
    if final_attempt['status_code'] != 200:
        logging.error(
            f"The {final_attempt['service_name']} returned a status code of "
            f"{final_attempt['status_code']} and a message of "
            f"{final_attempt['response_body']}. Full response: {response}"
        )
        return jsonify({
            'message': (
                f"The {final_attempt['service_name']} returned a status code "
                f"of {final_attempt['status_code']} and a message of "
                f"{final_attempt['response_body']}"
            ),
            'response_data': response
        }), 502

    logging.info(f'Email sent successfully. Full response: {response}')
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)
