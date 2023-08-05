from myst.client import Client
from myst.openapi.models.model_run_result_list import ModelRunResultList


def request_sync(client: Client, project_uuid: str, model_uuid: str) -> ModelRunResultList:
    """Lists model run results for the given model."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/models/{model_uuid}/run_results/",
        response_class=ModelRunResultList,
    )
