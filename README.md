# Rupa Health Coding Assessment - Email Abstraction Service

## Overview

This is a Flask API designed to send emails using either the Mailgun or Sendgrid email service providers. 

The API contains a single route, `/email` that accepts POST requests for sending emails. Request's JSON body containing the email data is validated and transformed before being used. If the sending process fails, the failure is logged and a status code 502 is returned. If the email is sent successfully, the success is logged and a status code 200 is returned.

The `EmailService` class has methods to send emails using Client SDKs of either Mailgun or Sendgrid. Delivery of email is retried up to a maximum of 3 times if it fails and the 'retry' attribute is True. The service can also switch to another provider and try sending the email again if the 'email_provider_fallback' attribute is True.

## Installation and Running

### Step 1: Set up a Python Virtual Environment

First, we need to set up a virtual environment in Python3. Virtual environment is a way of keeping the dependencies required by different projects separate by creating isolated Python virtual environments for them.

To create a virtual environment, navigate to the project directory from the terminal and run the following command:

```bash
python3 -m venv env
```

This will create a new virtual environment named 'env' in the current directory.

### Step 2: Activate the Virtual Environment

After creating the virtual environment, you need to activate it. The command to activate the virtual environment depends on your operating system:

#### On macOS and Linux:

```bash
source env/bin/activate
```

#### On Windows:

```bash
.\env\Scripts\activate
```

### Step 3: Install Packages

To install all the necessary packages, you will use pip, this is the standard package manager for Python. It will also be installed when creating the virtual environment.

Use the following command to install the required packages:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

To run the Flask application use:

```bash
flask run
```

The application will be running on http://127.0.0.1:5000

### Step 5: Add a .env File

Create a file named '.env' in the project root and add the following environment variables:

```
DEFAULT_EMAIL_PROVIDER = 'MAILGUN'
MAILGUN_API_KEY = '<MAILGUN_API_KEY>'
MAILGUN_DOMAIN = '<MAILGUN_DOMAIN>'
MAILGUN_API_URL = 'https://api.mailgun.net/v3'
SENDGRID_API_URL = 'https://api.sendgrid.com/v3'
SENDGRID_API_KEY = '<SENDGRID_API_KEY>'
MAX_RETRIES = 3
```

### Step 6: Run the Tests

To run the tests, make sure you're in the project root and use:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## API Documentation

### POST /email

#### Request Body

The request body should be a JSON object with the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| to | string | The email address of the recipient |
| to_name | string | The name of the recipient |
| from | string | The email address of the sender |
| from_name | string | The name of the sender |
| subject | string | The subject of the email |
| body | string | The body of the email |

**Request body example:**

```json
{
    "to": "recipient@example.com",
    "to_name": "Recipient Name",
    "from": "sender@example.com",
    "from_name": "Sender Name",
    "subject": "Email Subject",
    "body": "Email Body"
}
```

#### Query Parameters

| Parameter | Default | Type | Description |
| --- | --- | --- | --- |
| provider | MAILGUN | string | The email service provider to use. Currently only 'MAILGUN' and 'SENDGRID' are supported. |
| retry | false | boolean | Whether to retry sending the email if it fails. |
| email_provider_fallback | false | boolean | Whether to switch to another provider and try sending the email again if the first provider fails all retries. |

#### Response

| Status Code | Description |
| --- | --- |
| 200 | Email sent successfully |
| 400 | Invalid request body |
| 502 | Email sending failed |

**Response body examples:**

**Success:**
```json
{
    "message": "The SENDGRID returned a status code of 202 and a message of ",
    "response_data": {
        "attempts": [
            {
                "response_body": "",
                "service_name": "SENDGRID",
                "status_code": 202
            }
        ],
        "email_data": {
            "body": "Your Bill$10",
            "from_email": "camcardosi@mac.com",
            "from_name": "Cameron Cardosi",
            "subject": "A message from The Fake Family",
            "to_email": "fake@example.com",
            "to_name": "Mr. Fake"
        },
        "final_attempt": {
            "response_body": "",
            "service_name": "SENDGRID",
            "status_code": 202
        },
        "send_success": true
    }
}
```

**Failure:**
```json
{
    "message": "The MAILGUN returned a status code of 403 and a message of {\"message\":\"Domain sandboxe1d4f67b0d01443b84c0ede741584ce6.mailgun.org is not allowed to send: Free accounts are for test purposes only. Please upgrade or add the address to authorized recipients in Account Settings.\"}\n",
    "response_data": {
        "attempts": [
            {
                "response_body": "{\"message\":\"Domain sandboxe1d4f67b0d01443b84c0ede741584ce6.mailgun.org is not allowed to send: Free accounts are for test purposes only. Please upgrade or add the address to authorized recipients in Account Settings.\"}\n",
                "service_name": "MAILGUN",
                "status_code": 403
            }
        ],
        "email_data": {
            "body": "Your Bill$10",
            "from_email": "no-reply@fake.com",
            "from_name": "Ms. Fake",
            "subject": "A message from The Fake Family",
            "to_email": "fake@example.com",
            "to_name": "Mr. Fake"
        },
        "final_attempt": {
            "response_body": "{\"message\":\"Domain sandboxe1d4f67b0d01443b84c0ede741584ce6.mailgun.org is not allowed to send: Free accounts are for test purposes only. Please upgrade or add the address to authorized recipients in Account Settings.\"}\n",
            "service_name": "MAILGUN",
            "status_code": 403
        },
        "send_success": false
    }
}
```

## Example cURL requests:

Default provider (Mailgun):
```bash
curl --location 'http://127.0.0.1:5000/email' \
--header 'Content-Type: application/json' \
--data-raw '{
  "to": "fake@example.com",
  "to_name": "Mr. Fake",
  "from": "no-reply@fake.com",
  "from_name":"Ms. Fake",
  "subject": "A message from The Fake Family",
  "body": "<h1>Your Bill</h1><p>$10</p>"
}
'
```

Sendgrid provider with retry and fallback:
```bash
curl --location 'http://127.0.0.1:5000/email?emailProvider=SENDGRID&retry=True&emailProviderFallback=True' \
--header 'Content-Type: application/json' \
--data-raw '{
  "to": "fake@example.com",
  "to_name": "Mr. Fake",
  "from": "camcardosi@mac.com",
  "from_name":"Cameron Cardosi",
  "subject": "A message from The Fake Family",
  "body": "<h1>Your Bill</h1><p>$10</p>"
}
'
```


## Design Decisions

### Tools and Frameworks

- **Flask:** Flask is a lightweight WSGI web application framework. I chose Flask because it is a simple framework that is easy to set up and use. It is also very flexible and allows for easy integration with other tools.

- **Requests:** Requests is a simple HTTP library for Python. I chose Requests because it is a simple and elegant library that makes HTTP requests easy to use.

- **Python Dotenv:** Python Dotenv is a Python library that reads key-value pairs from a .env file and adds them to the environment variables.

### Time Spent

I spent roughly 4 hours on this project. There was a lot of starting and stoping due to other commitments, but I tried to keep track of the time spent.

### Extra Features

- Basic logging - which is printed to the console when running the application.
- Retry sending email if it fails.
- Switch to another provider and try sending the email again if the first provider fails all retries.

### Things to know

- Mailgun requires the recipient email address to be added to the authorized recipients list in the Mailgun dashboard. I intentionally did not add any authorized recipients to the Mailgun dashboard so that the Mailgun provider would fail and it would be easier to demonstrate the retry and fallback features.

