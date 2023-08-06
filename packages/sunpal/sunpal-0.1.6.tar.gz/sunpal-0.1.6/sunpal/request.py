import urllib
from sunpal import util, http_request
from sunpal.main import SunPal
from sunpal import compat
import json


def send_list_request(method, url, params=None, env=None, headers=None):
    serialized = {}

    if params is None:
        params = {}

    for k, v in list(params.items()):
        if isinstance(v, list):
            v = json.dumps(v)
        serialized.update({k: v})
    return send(method, url, serialized, env, headers)


def send(method, url, params=None, env=None, headers=None, file=None):
    ser_params = None
    if params and not file:
        ser_params = util.serialize(params)

    if file:
        ser_params = params

    env = env or SunPal.default_env
    response = http_request.request(method, url, env, ser_params, headers, file=file)
    from sunpal.result import Result
    from sunpal.list_result import ListResult

    if "results" in response:
        return ListResult(response["results"], response.get("next_offset", None))
    return Result(response)


def uri_path(*paths):
    url = ""
    for path in paths:
        if path is None or len(str(path).strip()) < 1:
            raise Exception("Id is None or empty")
        if compat.py_major_v >= 3:
            url = url + "/" + urllib.parse.quote(str(path).strip())
        else:
            url = url + "/" + urllib.quote(str(util.get_val(path)))
    return url + "/"
