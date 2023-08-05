from myst.client import Client
from myst.openapi.models.operation_create import OperationCreate
from myst.openapi.models.operation_get import OperationGet


def request_sync(client: Client, project_uuid: str, json_body: OperationCreate) -> OperationGet:
    """Creates an operation."""

    return client.request(
        method="post",
        path=f"/projects/{project_uuid}/operations/",
        response_class=OperationGet,
        request_model=json_body,
    )
