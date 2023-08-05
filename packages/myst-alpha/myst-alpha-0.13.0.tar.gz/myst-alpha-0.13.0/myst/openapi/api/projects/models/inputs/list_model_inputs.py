from myst.client import Client
from myst.openapi.models.input_list import InputList


def request_sync(client: Client, project_uuid: str, model_uuid: str) -> InputList:
    """Lists inputs for a model."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/models/{model_uuid}/inputs/", response_class=InputList
    )
