import unittest
from datetime import date

from src.matter_email import planned_email


class MatterEmailDecisionTest(unittest.TestCase):
    def test_signed_delivery_after_payment_takes_priority_over_deadline(self):
        matter = {
            "matter_id": "M-104",
            "client_email": "client@example.com",
            "payment_received": True,
            "signed_document_delivered": False,
            "deadline": "2026-08-12",
        }
        self.assertEqual(
            planned_email(matter, date(2026, 8, 10)),
            ("signed-document", "Signed document ready for matter M-104"),
        )

    def test_distant_unpaid_matter_has_no_message(self):
        matter = {
            "matter_id": "M-105",
            "client_email": "client@example.com",
            "payment_received": False,
            "signed_document_delivered": False,
            "deadline": "2026-09-01",
        }
        self.assertIsNone(planned_email(matter, date(2026, 8, 10)))


if __name__ == "__main__":
    unittest.main()
