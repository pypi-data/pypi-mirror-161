from myst.client import Client
from myst.openapi.models.user_get import UserGet


def request_sync(client: Client) -> UserGet:
    """Gets you."""

    return client.request(method="get", path=f"/users/me", response_class=UserGet)
