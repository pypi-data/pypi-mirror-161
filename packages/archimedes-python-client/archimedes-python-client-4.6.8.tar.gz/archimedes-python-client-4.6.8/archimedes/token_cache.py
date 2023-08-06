from msal_extensions import (
    FilePersistence,
    PersistedTokenCache,
    build_encrypted_persistence,
)

from .configuration import get_msal_path


def build_persistence(location, fallback_to_plaintext=False):
    """Build a suitable persistence instance based your current OS"""
    try:
        return build_encrypted_persistence(location)
    except:  # pylint:disable=bare-except
        if not fallback_to_plaintext:
            raise
        return FilePersistence(location)


def get_token_cache():
    """
    Returns token cache
    """
    persistence = build_persistence(get_msal_path(), True)
    return PersistedTokenCache(persistence)
