import abc
import pathlib
from abc import abstractmethod
from typing import Optional

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials as GoogleCredentials
from google.oauth2.service_account import IDTokenCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

import myst
from myst.auth.user_credentials_cache import UserCredentialsCache
from myst.settings import PROJECT_ROOT, settings


class Credentials(abc.ABC):
    """Abstraction around various types of credentials which enable use of the Myst API."""

    @property
    @abstractmethod
    def token(self) -> str:
        """Validated Bearer token using these credentials."""
        raise NotImplementedError()


class GoogleServiceAccountCredentials(Credentials):
    """Credentials that use a service account.

    API docs are here:
    https://google-auth.readthedocs.io/en/master/reference/google.oauth2.service_account.html
    """

    def __init__(self, key_file_path: Optional[pathlib.Path] = None, target_audience: Optional[str] = None):
        super().__init__()

        self._credentials = IDTokenCredentials.from_service_account_file(
            filename=key_file_path or settings.MYST_APPLICATION_CREDENTIALS,
            target_audience=target_audience or settings.MYST_API_HOST,
        )

    @property
    def credentials(self) -> IDTokenCredentials:
        """Underlying Google ID token credentials."""
        return self._credentials

    @property
    def token(self) -> str:
        """Validated Bearer token using these credentials."""
        if not self.credentials.valid:
            self.credentials.refresh(GoogleRequest())

        return self.credentials.token


class GoogleConsoleCredentials(Credentials):
    """Credentials created by sending the user through a local OAuth flow.

    API docs are here:
    https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html
    """

    CLIENT_SECRET_FILE = PROJECT_ROOT / "myst" / "data" / "google_oauth_client_not_so_secret.json"

    def __init__(self, use_console: bool = False, use_cache: bool = True) -> None:
        super().__init__()

        self._credentials = self._get_credentials(use_console=use_console, use_cache=use_cache)

    @property
    def credentials(self) -> GoogleCredentials:
        """Underlying Google credentials."""
        return self._credentials

    @property
    def token(self) -> str:
        """Validated Bearer token using these credentials."""
        if not self.credentials.valid:
            self.credentials.refresh(GoogleRequest())

        return self.credentials.id_token

    def _get_credentials(self, use_console: bool, use_cache: bool) -> GoogleCredentials:
        """Obtains credentials via cache or OAuth flow."""
        user_credentials_cache = UserCredentialsCache()

        # Note that this will also return `None` if user credentials were not found or couldn't be loaded from cache.
        user_credentials = user_credentials_cache.load() if use_cache else None

        if user_credentials:
            return user_credentials

        # Couldn't find user credentials in cache or explicitly told not to use cache, so perform the OAuth2.0 dance.
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=self.CLIENT_SECRET_FILE,
            scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        )
        user_credentials = flow.run_console() if use_console else flow.run_local_server()

        # Write newly fetched user credentials to cache.
        if use_cache:
            user_credentials_cache.save(user_credentials=user_credentials)

        return user_credentials


class FakeCredentials(Credentials):
    """Fake credentials for use in tests."""

    @property
    def token(self) -> str:
        return "fake-token"


def authenticate(credentials: Optional[Credentials] = None, use_console: bool = False, use_cache: bool = True) -> None:
    """Authenticates the global client with user credentials.

    Args:
        credentials: custom credentials to use instead of getting credentials from user account; if provided, this
            method will prefer these over other authentication methods
        use_console: whether or not to use the console for the user account authorization flow
        use_cache: whether or not to reuse cached user credentials
    """
    if credentials is None:
        credentials = GoogleConsoleCredentials(use_console=use_console, use_cache=use_cache)

    myst.get_client().authenticate(credentials=credentials)


def authenticate_with_service_account(key_file_path: Optional[pathlib.Path] = None) -> None:
    """Authenticates the global client with service account credentials.

    Args:
        key_file_path: absolute path to service account key file; if this is not given, this will look
            for the key file path in the `MYST_APPLICATION_CREDENTIALS` environment variable
    """
    client = myst.get_client()
    creds = GoogleServiceAccountCredentials(key_file_path=key_file_path, target_audience=client.base_url)
    client.authenticate(credentials=creds)
