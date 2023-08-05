from myst.client import Client
from myst.openapi.models.model_get import ModelGet
from myst.openapi.models.model_update import ModelUpdate


def request_sync(client: Client, project_uuid: str, uuid: str, json_body: ModelUpdate) -> ModelGet:
    """Updates a model."""

    return client.request(
        method="patch", path=f"/projects/{project_uuid}/models/{uuid}", response_class=ModelGet, request_model=json_body
    )
