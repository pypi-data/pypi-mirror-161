from myst.client import Client
from myst.openapi.models.model_create import ModelCreate
from myst.openapi.models.model_get import ModelGet


def request_sync(client: Client, project_uuid: str, json_body: ModelCreate) -> ModelGet:
    """Creates a model."""

    return client.request(
        method="post", path=f"/projects/{project_uuid}/models/", response_class=ModelGet, request_model=json_body
    )
