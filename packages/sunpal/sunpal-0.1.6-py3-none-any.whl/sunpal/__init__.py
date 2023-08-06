from sunpal.api_error import APIError, InvalidRequestError, OperationFailedError
from sunpal.models import *
from sunpal.main import SunPal


def configure(api_key, site):
    SunPal.configure(
        {
            "api_key": api_key,
            "site": site,
        }
    )


def update_connect_timeout_secs(connect_timeout):
    SunPal.update_connect_timeout_secs(connect_timeout)


def update_read_timeout_secs(read_timeout):
    SunPal.update_read_timeout_secs(read_timeout)
