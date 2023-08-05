from myst.client import Client
from myst.openapi.models.input_get import InputGet


def request_sync(client: Client, project_uuid: str, operation_uuid: str, uuid: str) -> InputGet:
    """Deletes an input for an operation."""

    return client.request(
        method="delete",
        path=f"/projects/{project_uuid}/operations/{operation_uuid}/inputs/{uuid}",
        response_class=InputGet,
    )
