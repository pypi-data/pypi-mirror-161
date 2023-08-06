import os
import sunpal
import unittest

api_key = os.environ.get("API_KEY_SUNPAL")
site = "sunwise"
sunpal.configure(api_key, site)


class ConsultaTestCase(unittest.TestCase):
    def test_generate_consulta(self):
        entry = sunpal.Consulta.create(
            {
                "reference": "proposal-uuid-sunwise",
                "rfc": "EAEN6506051Y8",
                "first_name": "NOVENTAYTRES",
                "second_name": "PRUEBA",
                "first_last_name": "EXPPAT",
                "second_last_name": "EXPMAT",
            }
        )

        self.assertTrue(entry.consulta, True)

    def test_get_buro_status(self):
        entry = sunpal.Consulta.retrieve(
            id="EAEN6506051Y8",
            params={"reference": "proposal-uuid-sunwise"},
        )
        self.assertTrue(entry.consulta, True)


if __name__ == "__main__":
    unittest.main()
