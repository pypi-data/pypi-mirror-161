from myst.client import Client
from myst.openapi.models.operation_get import OperationGet
from myst.openapi.models.operation_update import OperationUpdate


def request_sync(client: Client, project_uuid: str, uuid: str, json_body: OperationUpdate) -> OperationGet:
    """Updates an operation."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/operations/{uuid}",
        response_class=OperationGet,
        request_model=json_body,
    )
