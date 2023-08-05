from myst.client import Client
from myst.openapi.models.model_run_result_get import ModelRunResultGet


def request_sync(client: Client, project_uuid: str, model_uuid: str, uuid: str) -> ModelRunResultGet:
    """Gets a model run result by its unique identifier."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/models/{model_uuid}/run_results/{uuid}",
        response_class=ModelRunResultGet,
    )
