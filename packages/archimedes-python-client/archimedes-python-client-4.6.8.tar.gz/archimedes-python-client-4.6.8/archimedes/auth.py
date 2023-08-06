import os

import msal

from .configuration import get_api_config
from .token_cache import get_token_cache


def get_scopes():
    """
    Returns the default scopes url
    """
    api_app_id_uri_base = f"api://{get_api_config().aad_app_client_id}"
    return [
        f"{api_app_id_uri_base}/.default",
    ]


class NoneAuth(Exception):
    """User not logged in. Please log in using `arcl auth login <organization_id>"""


class ArchimedesPublicClientAuth:  # pylint:disable=too-few-public-methods
    """
    This class holds the client side auth application
    """

    def __init__(self, client_id, authority, cache=None):
        self.app = self.build_msal_app(client_id, authority, cache=cache)

    @staticmethod
    def build_msal_app(client_id, authority, cache=None):
        """
        Builds and returns an MSAL app for authentication
        Parameters:
            client_id:
            authority:
            cache:
        """
        return msal.PublicClientApplication(
            client_id,
            authority=authority,
            token_cache=cache,
        )


class ArchimedesLocalAuth(ArchimedesPublicClientAuth):
    """
    Auth app for local development
    """

    def __init__(self):
        api_config = get_api_config()
        super().__init__(api_config.client_id, api_config.authority, get_token_cache())

    def get_access_token_silent(self):
        """
        Returns access token
        """
        # We now check the cache to see
        # whether we already have some accounts
        # that the end user already used to sign in before.
        accounts = self.app.get_accounts()
        if not accounts:
            return None

        chosen = accounts[0]
        result = self.app.acquire_token_silent(get_scopes(), account=chosen)

        if result is None or "access_token" not in result:
            description = (
                f" Error details: {result['error_description']}"
                if result is not None and "error_description" in result
                else ""
            )
            raise NoneAuth(
                f"User not logged in. "
                f"Please log in using `arcl auth login <organization_id>`"
                f".{description}"
            )

        return result.get("access_token")


class ArchimedesConfidentialAuth:
    """
    Class for authentication methods for cloud deployment
    """

    def __init__(self, client_id, client_credential, authority):
        self.app = self.build_confidential_msal_app(
            client_id, client_credential, authority
        )

    def get_access_token_silent(self):
        """
        Returns access token
        """
        result = self.app.acquire_token_for_client(get_scopes())

        if result is None or "access_token" not in result:
            description = (
                f" Error details: {result['error_description']}"
                if result is not None and "error_description" in result
                else ""
            )
            raise NoneAuth(
                "Authentication failed. "
                "Please make sure that AZURE_AD_APP_ID, "
                "AZURE_AD_APP_CLIENT_CREDENTIAL and "
                f"AZURE_AD_TENANT_ID are properly configured.{description}"
            )

        return result.get("access_token")

    @staticmethod
    def build_confidential_msal_app(client_id, client_credential, authority):
        """
        Builds and returns MSAL app
        Parameters:
            client_id:
            client_credential:
            authority:
        """
        return msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_credential,
            authority=authority,
        )


def get_auth():
    """
    Creates and returns an auth application
    """
    archimedes_auth = None
    use_app_authentication = os.getenv(
        "USE_APP_AUTHENTICATION", "false"
    ).strip().lower() not in ["false", "f", "0"]
    use_web_authentication = os.getenv(
        "USE_WEB_AUTHENTICATION", "false"
    ).strip().lower() not in ["false", "f", "0"]
    assert not (
        use_app_authentication and use_web_authentication
    ), "Only one of USE_APP_AUTHENTICATION or USE_WEB_AUTHENTICATION can be set to TRUE"
    is_local = not use_app_authentication and not use_web_authentication
    if is_local:
        archimedes_auth = ArchimedesLocalAuth()
    else:
        azure_ad_tenant_id = os.getenv("AZURE_AD_TENANT_ID")
        azure_ad_client_id = os.getenv("AZURE_AD_APP_ID")
        azure_ad_authority = f"https://login.microsoftonline.com/{azure_ad_tenant_id}"

        if use_app_authentication:
            azure_ad_client_credential = os.getenv("AZURE_AD_APP_CLIENT_CREDENTIAL")
            archimedes_auth = ArchimedesConfidentialAuth(
                azure_ad_client_id, azure_ad_client_credential, azure_ad_authority
            )
        elif use_web_authentication:
            archimedes_auth = None
    return archimedes_auth
