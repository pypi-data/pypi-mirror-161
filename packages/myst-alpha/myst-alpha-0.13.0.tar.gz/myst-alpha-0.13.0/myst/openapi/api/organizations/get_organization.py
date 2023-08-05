from myst.client import Client
from myst.openapi.models.organization_get import OrganizationGet


def request_sync(client: Client, uuid: str) -> OrganizationGet:
    """Gets an organization by its unique identifier."""

    return client.request(method="get", path=f"/organizations/{uuid}", response_class=OrganizationGet)
