from sunpal.model import Model
from sunpal import request


class Consulta(Model):
    fields = [
        "id",
        "folio",
        "reference",
        "user",
    ]

    @staticmethod
    def create(params=None, env=None, headers=None):
        return request.send(
            "post", request.uri_path("burocredito/record"), params, env, headers
        )

    @staticmethod
    def retrieve(id, params, env=None, headers=None):
        return request.send(
            "get", request.uri_path("burocredito/record", id), params, env, headers
        )
