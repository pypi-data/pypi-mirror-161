from myst.client import Client
from myst.openapi.models.model_get import ModelGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> ModelGet:
    """Deletes a model."""

    return client.request(method="delete", path=f"/projects/{project_uuid}/models/{uuid}", response_class=ModelGet)
