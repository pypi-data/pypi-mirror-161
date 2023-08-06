import os
import sunpal
import unittest

api_key = os.environ.get("API_KEY_SUNPAL")
site = "sunwise"
sunpal.configure(api_key, site)


class RequestTestCase(unittest.TestCase):
    def test_get_customer(self):
        entry = sunpal.Customer.retrieve(
            id="EAEN6506051Y8",
            params={"reference": "proposal-uuid-sunwise"},
        )
        print()
        print(entry.customer.id)
        print(entry.customer.email)
        print(entry.customer.status.key)
        print(entry.customer.records.current)
        self.assertTrue(entry.customer, True)


if __name__ == "__main__":
    unittest.main()
