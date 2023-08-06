import sys

try:
    import simplejson as json  # noqua
except ImportError:
    import json  # noqua

py_major_v = sys.version_info[0]
py_minor_v = sys.version_info[1]

if py_major_v < 3:
    from urllib import urlencode  # noqua
    from urlparse import urlparse  # noqua
elif py_major_v >= 3:
    from urllib.parse import urlencode, urlparse  # noqua
