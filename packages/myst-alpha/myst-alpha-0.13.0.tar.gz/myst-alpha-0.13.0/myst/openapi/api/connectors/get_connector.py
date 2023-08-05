from myst.client import Client
from myst.openapi.models.connector_get import ConnectorGet


def request_sync(client: Client, uuid: str) -> ConnectorGet:
    """Gets a connector by its unique identifier."""

    return client.request(method="get", path=f"/connectors/{uuid}", response_class=ConnectorGet)
