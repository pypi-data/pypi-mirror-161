import os
import sunpal
import unittest

api_key = os.environ.get("API_KEY_SUNPAL")
site = "sunwise"
sunpal.configure(api_key, site)


class TestCases(unittest.TestCase):
    def test_retrieve(self):
        entry = sunpal.Interactive.retrieve("238754ef-fc8d-469c-859d-caa029e3cb23")
        # print()
        # print(entry.interactive)
        self.assertTrue(hasattr(entry.interactive, "id"), True)

    def test_create(self):
        entry = sunpal.Interactive.create(
            {
                "proposal_ref_id": "238754ef-fc8d-469c-859d-caa029e3cb23",
                "proposal_creation_date": "2022-07-29",
                "client_full_name": "Abner Grajales",
                "project_name": "Project Name",
                "company_ref_id": "d7d161bc-b398-47e9-a5df-102bf3cc9e39",
                "company_name": "Company Name",
                "compay_logo_url": "https://static.intercomassets.com/avatars/3486213/square_128/custom_avatar-1611956778.png",
            }
        )

        self.assertTrue(hasattr(entry.interactive, "id"), True)

    def test_delete(self):
        sunpal.Interactive.delete("238754ef-fc8d-469c-859d-caa029e3cb23")
        self.assertTrue(True, True)

    def test_update(self):

        entry = sunpal.Interactive.update(
            "238754ef-fc8d-469c-859d-caa029e3cb23",
            {
                "client_full_name": "Nombre del Contacto",
                "has_permalink": True,
                "project_name": "Project Name",
                "company_name": "Company Name",
                "compay_logo_url": "https://static.intercomassets.com/avatars/3486213/square_128/custom_avatar-1611956778.png",
            },
        )

        self.assertTrue(hasattr(entry.interactive, "id"), True)

    def test_retrieve_signature(self):
        entry = sunpal.Interactive.retrieve_signature(
            "238754ef-fc8d-469c-859d-caa029e3cb23"
        )
        print("entry.holograph", entry.holograph.signature)
        self.assertTrue(True, True)

    def test_retrieve_datasheets(self):
        entry = sunpal.Interactive.retrieve_datasheets(
            params={"proposal_ref_id": "238754ef-fc8d-469c-859d-caa029e3cb23"}
        )
        print("entry.datasheets", entry)
        self.assertTrue(True, True)

    def test_add_datasheet(self):
        entry = sunpal.Interactive.add_datasheet(
            {
                "proposal_ref_id": "238754ef-fc8d-469c-859d-caa029e3cb23",
                "type": "panels",
                "name": "AE350M6_72",
            },
            file={"archive": open("/tmp/example.txt", "rb")},
        )

        print("entry.datasheet", entry.datasheet)
        self.assertTrue(True, True)

    def test_delete_datasheet(self):
        sunpal.Interactive.delete_datasheet(
            id="ed684016-4aa1-4d7f-9d88-42911fee268e",
            params={"proposal_ref_id": "238754ef-fc8d-469c-859d-caa029e3cb23"},
        )
        self.assertTrue(True, True)

    def test_retrieve_documments(self):
        entry = sunpal.Interactive.retrieve_documments(
            params={"proposal_ref_id": "238754ef-fc8d-469c-859d-caa029e3cb23"}
        )
        print("entry.documments", entry)
        self.assertTrue(True, True)

    def test_add_documments(self):
        entry = sunpal.Interactive.add_documment(
            {
                "proposal_ref_id": "238754ef-fc8d-469c-859d-caa029e3cb23",
                "document_reference_id": "987754ef-fc8d-469c-859d-caa029e3ex55",
                "name": "Smart Documment Demo",
            }
        )

        print("entry.documment", entry.documment)
        self.assertTrue(True, True)

    def test_delete_documment(self):
        sunpal.Interactive.delete_documment(
            id="86e30d54-9966-489d-92af-79a53b9db1ee",
            params={"proposal_ref_id": "238754ef-fc8d-469c-859d-caa029e3cb23"},
        )
        self.assertTrue(True, True)

    def test_remove_approbal(self):
        sunpal.Interactive.remove_approbal("238754ef-fc8d-469c-859d-caa029e3cb23")
        self.assertTrue(True, True)

    def test_revoke_signature(self):
        sunpal.Interactive.revoke_signature("238754ef-fc8d-469c-859d-caa029e3cb23")
        self.assertTrue(True, True)


if __name__ == "__main__":
    unittest.main()
