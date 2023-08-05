from myst.client import Client
from myst.openapi.models.operation_get import OperationGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> OperationGet:
    """Deletes an operation."""

    return client.request(
        method="delete", path=f"/projects/{project_uuid}/operations/{uuid}", response_class=OperationGet
    )
