from sunpal.model import Model
from sunpal import request


class Customer(Model):
    class StatusItem(Model):
        fields = ["key", "value"]

    class RecordItem(Model):
        fields = ["current", "limit"]

    fields = [
        "id",
        "first_name",
        "last_name",
        "email",
        "status",
    ]

    @staticmethod
    def create(params=None, env=None, headers=None):
        return request.send(
            "post", request.uri_path("accounts/register-customer"), params, env, headers
        )

    @staticmethod
    def send_nip(params=None, env=None, headers=None):
        return request.send(
            "post",
            request.uri_path("accounts/resend/authorization"),
            params,
            env,
            headers,
        )

    @staticmethod
    def list(params=None, env=None, headers=None):
        return request.send_list_request(
            "get", request.uri_path("customers/customer/"), params, env, headers
        )

    @staticmethod
    def retrieve(id, params=None, env=None, headers=None):
        return request.send(
            "get", request.uri_path("accounts/customer", id), params, env, headers
        )

    @staticmethod
    def retrieve_by_reference(id, params=None, env=None, headers=None):
        return request.send(
            "get",
            request.uri_path("accounts/customer-by-reference", id),
            params,
            env,
            headers,
        )

    @staticmethod
    def update(id, params=None, env=None, headers=None):
        return request.send(
            "patch", request.uri_path("accounts/customer", id), params, env, headers
        )

    @staticmethod
    def add_address(id, params, env=None, headers=None):
        params.update({"customer_id": id})
        return request.send("post", "/accounts/address/", params, env, headers)

    @staticmethod
    def update_address(id, params, env=None, headers=None):
        return request.send("patch", f"/accounts/address/{id}/", params, env, headers)

    @staticmethod
    def delete_address(id):
        return request.send("delete", f"/accounts/address/{id}/")
