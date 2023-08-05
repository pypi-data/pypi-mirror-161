from typing import Any, Dict, Optional, Type, TypeVar

import httpx
import pydantic

from myst.auth.credentials import Credentials
from myst.models.base_model import BaseModel
from myst.models.exceptions import MystAPIError, MystClientError, NotFound, UnauthenticatedError
from myst.models.http_errors import HTTPValidationError, StringDetailError
from myst.settings import settings
from myst.version import get_package_version

RequestModelType = TypeVar("RequestModelType", bound=BaseModel)
ResponseModelType = TypeVar("ResponseModelType", bound=BaseModel)


class Client:
    """HTTP client for interacting with the Myst Platform API."""

    API_VERSION = "v1alpha2"
    USER_AGENT_PREFORMAT = "Myst/{api_version} PythonBindings/{package_version}"

    def __init__(
        self, credentials: Optional[Credentials] = None, timeout: Optional[int] = None, api_host: Optional[str] = None
    ):
        """A wrapper object providing convenient API access with credentials."""
        # Construct an httpx client so that we can reuse a single TCP connection and configuration.
        self.base_url = (api_host or settings.MYST_API_HOST).rstrip("/")
        self._client = httpx.Client(
            timeout=timeout or settings.API_TIMEOUT_SEC,
            headers={"User-Agent": self.user_agent},
            base_url=f"{self.base_url}/{self.API_VERSION}",
        )
        self._credentials = credentials

    def __del__(self) -> None:
        """Cleans up underlying client resources."""
        try:
            self._client.close()
        except Exception:
            # We aren't too concerned with issues that occur while cleaning up connections.
            pass

    def authenticate(self, credentials: Credentials) -> None:
        """Authenticates this client using the given credentials."""
        self._credentials = credentials

    @property
    def user_agent(self) -> str:
        """Gets the `User-Agent` header string to send to the Myst API."""
        # Infer Myst API version and Myst Python client library version for current active versions.
        return self.USER_AGENT_PREFORMAT.format(api_version=self.API_VERSION, package_version=get_package_version())

    def _get_credentials(self) -> Credentials:
        if self._credentials is None:
            raise UnauthenticatedError("No client credentials provided.")

        return self._credentials

    def request(
        self,
        method: str,
        path: str,
        response_class: Type[ResponseModelType],
        params: Optional[Dict[str, Any]] = None,
        request_model: Optional[RequestModelType] = None,
    ) -> ResponseModelType:
        """Executes a request for the given HTTP method and URL, handling JSON serialization and deserialization.

        Args:
            method: HTTP verb to execute, e.g. "GET", "POST", etc.
            path: path relative to the base URL, e.g. "/time_series/"
            response_class: name of the model class to parse the response content into
            params: HTTP query parameters
            request_model: JSON-able model instance to pass in request body

        Raises:
            MystClientError: client error (HTTP 4xx), including further details in the case of 422
            MystAPIError: server error (HTTP 500)
            NotFound: client error (HTTP 404)
            NotImplementedError: if a status code isn't handled by this method

        Returns:
            parsed and validated instance of indicated response class
        """
        # Convert the Pydantic request model into JSON form.
        content = request_model.json(exclude_unset=True, by_alias=True) if request_model else None

        # Make the API request.
        response = self._client.request(
            method=method,
            url=path,
            params=params,
            headers={"content-type": "application/json", "Authorization": f"Bearer {self._get_credentials().token}"},
            content=content,
        )

        # Handle the httpx response.
        if response.status_code in (200, 201):
            return response_class.parse_raw(response.content)
        elif response.status_code == 422:
            # Special-case 422 validation errors.
            try:
                raise MystClientError(HTTPValidationError.parse_raw(response.content))
            except pydantic.ValidationError:
                raise MystClientError(StringDetailError.parse_raw(response.content))
        elif response.status_code == 404:
            raise NotFound(message=StringDetailError.parse_raw(response.content).detail)
        elif 400 <= response.status_code < 500:
            # All other client errors.
            raise MystClientError(response.json())
        elif response.status_code == 500:
            raise MystAPIError(status_code=response.status_code, message="Internal server error")
        else:
            raise NotImplementedError()


# Lazily instantiate the global client so that we don't form a connection pool at import time.
_client: Optional[Client] = None


def get_client() -> Client:
    """Returns the global Myst client instance."""
    global _client

    if _client is None:
        _client = Client()

    return _client


def set_client(client: Client) -> None:
    """Sets the global Myst client instance.

    Useful for e.g. configuring timeouts globally.

    Args:
        client: the client to use
    """
    global _client

    _client = client
