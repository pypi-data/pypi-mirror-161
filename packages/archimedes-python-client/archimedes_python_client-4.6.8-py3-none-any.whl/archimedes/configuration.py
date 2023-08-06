import abc
import os

import pandas as pd

# Global archimedes config
USER_HOME_DIR = os.path.expanduser("~")
ARCHIMEDES_CONF_DIR = os.path.join(USER_HOME_DIR, ".archimedes")
DEFAULT_ENVIRONMENT = "prod"
DEFAULT_TIMEOUT_IN_SECONDS = "120"  # 2 minutes


def get_environment():
    """
    Returns the environment identifier for the application
    """
    env = os.environ.get(
        "ARCHIMEDES_ENVIRONMENT", os.environ.get("ENVIRONMENT", DEFAULT_ENVIRONMENT)
    )
    return env.strip().lower()


def get_api_timeout():
    """
    Returns the default timeout for all API requests
    """
    return int(os.getenv("ARCHIMEDES_API_TIMEOUT", DEFAULT_TIMEOUT_IN_SECONDS))


def get_msal_path():
    """
    Returns the path where MSAL cache file is stored
    """
    msal_path = os.path.join(ARCHIMEDES_CONF_DIR, f"msal-{get_environment()}.cache.bin")
    return msal_path


ARCHIMEDES_API_CONFIG = {
    "prod": {
        "client_id": "5bc3a702-d753-43ff-9051-e7fdfdd95023",
        "aad_app_client_id": "c0a9f773-6276-4d71-8df6-7239e695aff6",
        "url": "https://api.fabapps.io",
        "authority": "https://login.microsoftonline.com/common",
    },
    "dev": {
        "client_id": "2e2f3c84-d1aa-49cc-90a2-fd3fa3380d27",
        "aad_app_client_id": "eaaa9f9f-395d-46aa-847f-b5fb6c087ff6",
        "url": "https://api-dev.fabapps.io",
        "authority": "https://login.microsoftonline.com/common",
    },
}


class ArchimedesConstants:  # pylint:disable=too-few-public-methods
    """
    Defines the default constraints for the application
    """

    DATE_LOW = pd.to_datetime("1900-01-01T00:00:00+00:00")
    DATE_HIGH = pd.to_datetime("2090-01-01T00:00:00+00:00")


class InvalidEnvironmentException(Exception):
    """
    Exception to be raised when the environment to be
    """


class ApiConfig(abc.ABC):  # pylint:disable=too-few-public-methods
    """
    Base class for API config
    """

    def __init__(self, env):
        self.config = ARCHIMEDES_API_CONFIG
        if env not in self.config:
            raise InvalidEnvironmentException(
                f"Invalid environment {env}, "
                f"supported values are "
                f"{', '.join([str(key) for key in self.config])}"
            )
        self.environment = env.lower()

    def __getattr__(self, item):
        env_config = self.config[self.environment]
        return env_config[item]


def get_api_config():
    """
    Returns API configuration
    """
    return ApiConfig(get_environment())


def get_api_base_url(api_version: int) -> str:
    """
    Returns base url of the api

    Parameters:
        api_version: Version of the API
    """
    return f"{get_api_config().url}/v{api_version}"
