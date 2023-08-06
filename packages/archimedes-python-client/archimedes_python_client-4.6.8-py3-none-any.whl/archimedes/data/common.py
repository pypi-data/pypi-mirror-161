from functools import partial

from archimedes.configuration import get_api_base_url

API_VERSION = 2
get_api_base_url_v2 = partial(get_api_base_url, API_VERSION)
