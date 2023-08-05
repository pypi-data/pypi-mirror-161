from myst.client import Client
from myst.openapi.models.operation_get import OperationGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> OperationGet:
    """Gets an operation by its unique identifier."""

    return client.request(method="get", path=f"/projects/{project_uuid}/operations/{uuid}", response_class=OperationGet)
