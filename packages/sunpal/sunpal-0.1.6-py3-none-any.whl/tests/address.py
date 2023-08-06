import os
import sunpal
import unittest

api_key = os.environ.get("API_KEY_SUNPAL")
site = "sunwise"
sunpal.configure(api_key, site)


class AddressTestCase(unittest.TestCase):
    def setUp(self):
        self.customer_id = "GACA910614A36"
        item = sunpal.Customer.add_address(
            self.customer_id,
            {
                "street": "Calle 52 #611 x 87 y 89",
                "suburb": "Col. Centro",
                "city": "Mérida",
                "state": "Yuc",
                "favorite": True,
            },
        )
        self.address_id = item.address.id

    def test_update_address(self):
        item = sunpal.Customer.update_address(
            self.address_id,
            {
                "customer_id": self.customer_id,
                "street": "Calle 52 #611 x 87 y 89",
                "suburb": "Col. Centro",
                "city": "Mérida",
                "state": "Yuc",
                "favorite": True,
            },
        )
        self.assertTrue(item, True)

    def test_delete_address(self):
        item = sunpal.Customer.delete_address(self.address_id)
        self.assertTrue(item, True)

    # def tearDown(self):
    #     self.widget.dispose()


# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(AddressTestCase('test_update_address'))
#     suite.addTest(AddressTestCase('test_delete_address'))
#     return suite

# if __name__ == "__main__":
#     runner = unittest.TextTestRunner(failfast=True)
#     runner.run(suite())

if __name__ == "__main__":
    unittest.main()
