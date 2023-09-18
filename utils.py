import re
from email_types import EmailData


def validate_data(data: dict) -> None:
    """Validate the input."""
    required_fields = ["to", "to_name", "from", "from_name", "subject", "body"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )


def transform_data(data: dict) -> EmailData:
    """Convert the body HTML to plain text and rename keys."""
    data["body"] = re.sub('<[^<]+?>', '', data["body"])

    # Rename keys
    data['to_email'] = data.pop('to')
    data['from_email'] = data.pop('from')

    return data
