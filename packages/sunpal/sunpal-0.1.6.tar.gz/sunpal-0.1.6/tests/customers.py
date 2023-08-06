import os
import sunpal
import unittest

api_key = os.environ.get("API_KEY_SUNPAL")
site = "sunwise"
sunpal.configure(api_key, site)


class CustomersTestCase(unittest.TestCase):

    # def test_create_customer(self):
    #     import random

    #     rfc = "".join(random.choice("0123456789ABCDEF") for i in range(13))
    #     item = sunpal.Customer.create(
    #         {
    #             "first_name": "Jason",
    #             "last_name": "Bates",
    #             "second_surname": "Doub",
    #             "rfc": rfc,
    #             "email": "examplesw@yopmail.com",
    #         }
    #     )
    #     self.assertTrue(item, True)

    # def test_create_same_customer(self):

    #     item = sunpal.Customer.create(
    #         {
    #             "first_name": "Jason",
    #             "last_name": "Bates",
    #             "second_surname": "Doub",
    #             "rfc": "GACA910614A36",
    #             "email": "examplesw@yopmail.com",
    #         }
    #     )
    #     self.assertTrue(item, False)

    def test_get_customer(self):
        entry = sunpal.Customer.retrieve(
            id="EAEN6506051Y8",
            params={"reference": "proposal-uuid-sunwise"},
        )
        self.assertTrue(entry.customer, True)

    def test_get_customer_only_by_reference(self):
        entry = sunpal.Customer.retrieve_by_reference("proposal-uuid-sunwise")
        self.assertTrue(entry.customer, True)

    def test_get_dont_customer_exists(self):
        entry = sunpal.Customer.retrieve("ZACE950614A30")
        self.assertTrue(entry, False)


if __name__ == "__main__":
    unittest.main()
