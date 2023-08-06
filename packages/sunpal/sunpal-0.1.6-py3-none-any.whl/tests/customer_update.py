import os
import sunpal
import unittest

api_key = os.environ.get("API_KEY_SUNPAL")
site = "sunwise"
sunpal.configure(api_key, site)


class UpdateCustomerTestCase(unittest.TestCase):
    def test_send_new_nip(self):
        entry = sunpal.Customer.update(
            "EAEN6506051Y8",
            {
                "first_name": "NOVENTAYTRES",
                "second_name": "PRUEBA",
                "first_last_name": "EXPPAT",
                "second_last_name": "EXPMAT",
            },
        )

        self.assertTrue(entry.customer, True)


if __name__ == "__main__":
    unittest.main()
