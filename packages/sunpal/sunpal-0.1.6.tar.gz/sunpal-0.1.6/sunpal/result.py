from sunpal.compat import json
from sunpal.models import Customer, Consulta, Interactive


class Result(object):
    def __init__(self, response):
        self._response = response
        self._response_obj = {}

    @property
    def holograph(self):
        return self._get("holograph", Interactive.Signature, {})

    @property
    def documment(self):
        return self._get("documment", Interactive.Documment, {})

    @property
    def datasheet(self):
        return self._get("datasheets", Interactive.DataSheet, {})

    @property
    def datasheets(self):
        return self._get_list("datasheets", Interactive.DataSheet, [])

    @property
    def interactive(self):
        return self._get("interactive", Interactive, {})

    @property
    def consulta(self):
        return self._get("consulta", Consulta, {})

    @property
    def address(self):
        return self._get("address", Customer, {})

    @property
    def customer(self):
        return self._get(
            "customer",
            Customer,
            {"status": Customer.StatusItem, "records": Customer.RecordItem},
        )

    def _get_list(
        self, type, cls, sub_types={}, dependant_types={}, dependant_sub_types={}
    ):
        if not type in self._response:
            return None

        set_val = []
        for obj in self._response[type]:
            if isinstance(obj, dict):
                model = cls.construct(obj, sub_types, dependant_types)
                for k in dependant_sub_types:
                    model.init_dependant(obj, k, dependant_sub_types[k])
                set_val.append(model)

        self._response_obj[type] = set_val
        return self._response_obj[type]

    def _get(self, type, cls, sub_types=None, dependant_types=None):
        if self._response == {}:
            return None
        return cls.construct(self._response, sub_types, dependant_types)

        # Mapeo por objetos en el resultado
        # if not type in self._response:
        #     return None

        # if not type in self._response_obj:
        #     self._response_obj[type] = cls.construct(
        #         self._response[type], sub_types, dependant_types
        #     )
        # return self._response_obj[type]

    def __str__(self):
        return json.dumps(self._response, indent=4)


class Content(Result):
    pass
