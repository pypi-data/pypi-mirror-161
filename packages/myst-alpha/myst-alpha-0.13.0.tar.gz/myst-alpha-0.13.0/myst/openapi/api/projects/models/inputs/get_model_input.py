from myst.client import Client
from myst.openapi.models.input_get import InputGet


def request_sync(client: Client, project_uuid: str, model_uuid: str, uuid: str) -> InputGet:
    """Gets a specific input for a model."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/models/{model_uuid}/inputs/{uuid}", response_class=InputGet
    )
