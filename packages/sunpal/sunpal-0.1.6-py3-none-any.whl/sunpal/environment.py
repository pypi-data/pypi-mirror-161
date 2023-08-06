import os


class Environment(object):

    sunpal_domain = "test.sunpal.mx"
    protocol = "https"
    if "LOCAL_SUNPAL_DOMAIN" in os.environ:
        sunpal_domain = os.environ.get("LOCAL_SUNPAL_DOMAIN")
        protocol = "http"

    API_VERSION = "v1"
    connect_timeout = 30
    read_timeout = 80

    def __init__(self, options):
        self.api_key = options["api_key"]
        self.site = options["site"]

        if self.sunpal_domain is None:
            self.api_endpoint = "https://%s/api/%s" % (
                # self.site,
                self.sunpal_domain,
                self.API_VERSION,
            )
        else:
            self.api_endpoint = "http://%s/api/%s" % (
                # self.site,
                self.sunpal_domain,
                self.API_VERSION,
            )

    def api_url(self, url):
        # print(self.api_endpoint + url)
        return self.api_endpoint + url
