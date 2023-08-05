from myst.client import Client
from myst.openapi.models.model_get import ModelGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> ModelGet:
    """Gets a model by its unique identifier."""

    return client.request(method="get", path=f"/projects/{project_uuid}/models/{uuid}", response_class=ModelGet)
