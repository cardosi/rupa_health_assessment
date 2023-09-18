from typing import Literal, TypedDict, List


class EmailData(TypedDict):
    to_email: str
    to_name: str
    from_email: str
    from_name: str
    subject: str
    body: str


class EmailAttemptData(TypedDict):
    status_code: int
    service_name: str
    response_body: str


class ResponseData(TypedDict):
    email_data: EmailData
    attempts: List[EmailAttemptData]
    send_success: bool
    final_attempt: EmailAttemptData


EmailProvider = Literal['MAILGUN', 'SENDGRID']
