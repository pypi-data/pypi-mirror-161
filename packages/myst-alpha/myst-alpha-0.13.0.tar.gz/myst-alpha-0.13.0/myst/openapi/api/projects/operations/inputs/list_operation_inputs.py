from myst.client import Client
from myst.openapi.models.input_list import InputList


def request_sync(client: Client, project_uuid: str, operation_uuid: str) -> InputList:
    """Lists inputs for an operation."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/operations/{operation_uuid}/inputs/", response_class=InputList
    )
