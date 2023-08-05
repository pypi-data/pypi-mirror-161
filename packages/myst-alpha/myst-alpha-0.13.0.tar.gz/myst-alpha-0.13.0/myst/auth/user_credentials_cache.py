"""This module contains the `UserCredentialsCache` class."""
import json
import os
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials as GoogleCredentials


class UserCredentialsCache:
    """User credentials cache class for saving and loading user credentials to a local cache.

    This writes user credentials to a subdirectory within the `~/.config` directory (or `APPDATA` on Windows).
    """

    _CACHE_DIRNAME = "myst"
    _USER_CREDENTIALS_FILENAME = "myst_user_credentials.json"
    _USER_HOME_DIR = Path("~").expanduser()
    _CONFIG_HIDDEN = ".config"

    @property
    def cache_file_dir(self) -> Path:
        """Directory where we'll save the cached credentials."""
        if os.name == "nt":  # needed for Windows.
            return Path(os.environ["APPDATA"])
        else:
            return self._USER_HOME_DIR / self._CONFIG_HIDDEN

    @property
    def cache_file_path(self) -> Path:
        """Where to cache the user credentials in the local filesystem."""
        return self.cache_file_dir / self._CACHE_DIRNAME / self._USER_CREDENTIALS_FILENAME

    def load(self) -> Optional[GoogleCredentials]:
        """Loads credentials from cache.

        Returns:
            user_credentials or None if we could not not load them for some reason (eg. they didn't exist, they were
                malformed, etc.)
        """
        if not self.cache_file_path.exists():
            return None

        with self.cache_file_path.open("r") as user_credentials_file:
            user_credentials_json = json.load(user_credentials_file)

        # Note that we don't save the OAuth 2.0 access token, so we're explicitly setting it to None here.
        user_credentials = GoogleCredentials(token=None, **user_credentials_json)
        return user_credentials

    def save(self, user_credentials: GoogleCredentials) -> None:
        """Saves user credentials to cache."""
        cache_dir_path = self.cache_file_path.parent
        if not cache_dir_path.exists():
            cache_dir_path.mkdir(parents=True)

        # Note that we don't save the OAuth 2.0 access token, so we're explicitly not passing it in here.
        user_credentials_json = {
            "refresh_token": user_credentials.refresh_token,
            "id_token": user_credentials.id_token,
            "token_uri": user_credentials.token_uri,
            "client_id": user_credentials.client_id,
            "client_secret": user_credentials.client_secret,
            "scopes": user_credentials.scopes,
        }

        with self.cache_file_path.open("w") as cache_file:
            json.dump(user_credentials_json, cache_file)

    def clear(self) -> None:
        """Clears the user credentials cache."""
        self.cache_file_path.unlink()
