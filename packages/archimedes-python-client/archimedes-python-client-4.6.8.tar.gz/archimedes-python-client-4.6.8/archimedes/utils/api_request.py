"""
A collection of functions for integrating with the Archimedes API
"""
import json
from http import HTTPStatus

import requests
from requests.exceptions import (  # pylint:disable=redefined-builtin
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    JSONDecodeError,
    Timeout,
)
from retry import retry

from archimedes import NoneAuth, get_auth
from archimedes.configuration import get_api_timeout

RETRY_EXCEPTIONS = (ConnectionError, ConnectTimeout, HTTPError, Timeout)


class ArchimedesApi:  # pylint:disable=too-few-public-methods
    """
    Make request to the Archimedes API
    """

    def __init__(self):
        self.session = requests.Session()

    @retry(RETRY_EXCEPTIONS, tries=3, delay=2)
    def request(self, url, method="GET", access_token=None, **kwargs):
        """
        Make request to the Archimedes API. It automatically retries 3 times on failure.

        Args:
            url:
                full URL of the API endpoint.
            method:
                HTTP method to use.
            access_token:
                authorization token; if None, tries to get the token automatically based
                on the authentication configuration.
            **kwargs:
                other kwargs to requests.request.

        Returns:
            JSON response
        """
        if access_token is None:
            archimedes_auth = get_auth()
            if archimedes_auth is None:
                raise NoneAuth(
                    "access_token parameter must be passed when using "
                    "USE_WEB_AUTHENTICATION"
                )
            access_token = archimedes_auth.get_access_token_silent()

        timeout = kwargs.pop("timeout", get_api_timeout())
        kwargs["timeout"] = timeout

        headers = kwargs.pop("headers", {})

        headers.update({"Authorization": f"Bearer {access_token}"})
        response = self.session.request(method, url, headers=headers, **kwargs)

        if response.status_code not in [HTTPStatus.OK, HTTPStatus.CREATED]:
            try:
                response_json = response.json()
                if "message" in response_json:
                    error_message = response_json.get("message")
                elif "detail" in response_json:
                    error_message = response_json.get("detail")
                else:
                    error_message = json.dumps(response_json)
            except JSONDecodeError:
                error_message = response.content
            params_str = json.dumps(kwargs.get("params"))
            raise HTTPError(
                f"API Error while requesting {url} with parameters {params_str}: "
                f"{error_message}"
            )

        return response.json()


api = ArchimedesApi()
