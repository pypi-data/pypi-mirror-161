from myst.client import Client
from myst.openapi.models.organization_create import OrganizationCreate
from myst.openapi.models.organization_get import OrganizationGet


def request_sync(client: Client, json_body: OrganizationCreate) -> OrganizationGet:
    """Creates an organization."""

    return client.request(
        method="post", path=f"/organizations/", response_class=OrganizationGet, request_model=json_body
    )
