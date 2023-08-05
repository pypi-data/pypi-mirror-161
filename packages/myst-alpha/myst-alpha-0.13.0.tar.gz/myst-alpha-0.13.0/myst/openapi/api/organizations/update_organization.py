from myst.client import Client
from myst.openapi.models.organization_get import OrganizationGet
from myst.openapi.models.organization_update import OrganizationUpdate


def request_sync(client: Client, uuid: str, json_body: OrganizationUpdate) -> OrganizationGet:
    """Updates an organization."""

    return client.request(
        method="patch", path=f"/organizations/{uuid}", response_class=OrganizationGet, request_model=json_body
    )
