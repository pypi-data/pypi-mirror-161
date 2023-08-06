import os
import sunpal
import unittest

api_key = os.environ.get("API_KEY_SUNPAL")
site = "sunwise"
sunpal.configure(api_key, site)


class SendNipTestCase(unittest.TestCase):
    def test_send_new_nip(self):
        entry = sunpal.Customer.send_nip({"rfc": "EAEN6506051Y8"})
        self.assertTrue(entry.customer, True)


if __name__ == "__main__":
    unittest.main()
