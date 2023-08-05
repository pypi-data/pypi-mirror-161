from myst.client import Client
from myst.openapi.models.user_get import UserGet


def request_sync(client: Client, uuid: str) -> UserGet:
    """Gets the requested user."""

    return client.request(method="get", path=f"/users/{uuid}", response_class=UserGet)
