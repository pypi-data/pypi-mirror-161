from myst.client import Client
from myst.openapi.models.input_get import InputGet
from myst.openapi.models.input_update import InputUpdate


def request_sync(client: Client, project_uuid: str, model_uuid: str, uuid: str, json_body: InputUpdate) -> InputGet:
    """Updates an existing input for a model."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/models/{model_uuid}/inputs/{uuid}",
        response_class=InputGet,
        request_model=json_body,
    )
