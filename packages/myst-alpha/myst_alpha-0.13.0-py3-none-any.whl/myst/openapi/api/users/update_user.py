from myst.client import Client
from myst.openapi.models.user_get import UserGet
from myst.openapi.models.user_update import UserUpdate


def request_sync(client: Client, uuid: str, json_body: UserUpdate) -> UserGet:
    """Updates a user."""

    return client.request(method="patch", path=f"/users/{uuid}", response_class=UserGet, request_model=json_body)
