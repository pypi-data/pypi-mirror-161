from myst.client import Client
from myst.openapi.models.model_fit_result_list import ModelFitResultList


def request_sync(client: Client, project_uuid: str, model_uuid: str) -> ModelFitResultList:
    """Lists model fit results for the given model."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/models/{model_uuid}/fit_results/",
        response_class=ModelFitResultList,
    )
