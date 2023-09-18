import unittest
from utils import validate_data, transform_data


class TestUtilFunctions(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            "to": "test@example.com",
            "to_name": "Test User",
            "from": "sender@example.com",
            "from_name": "Sender User",
            "subject": "Test Subject",
            "body": "<p>Hello, World!</p>"
        }

    def test_validate_data(self):
        # Test with valid data
        try:
            validate_data(self.valid_data)
        except ValueError:
            self.fail("validate_data() raised ValueError unexpectedly!")

        # Test with missing fields
        invalid_data = self.valid_data.copy()
        del invalid_data["to"]
        with self.assertRaises(ValueError):
            validate_data(invalid_data)

    def test_transform_data(self):
        transformed_data = transform_data(self.valid_data.copy())
        self.assertEqual(transformed_data["body"], "Hello, World!")
        self.assertEqual(transformed_data["to_email"], "test@example.com")
        self.assertEqual(transformed_data["from_email"], "sender@example.com")


if __name__ == '__main__':
    unittest.main()
