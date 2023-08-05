from myst.client import Client
from myst.openapi.models.organization_list import OrganizationList


def request_sync(client: Client) -> OrganizationList:
    """Lists organizations."""

    return client.request(method="get", path=f"/organizations/", response_class=OrganizationList)
