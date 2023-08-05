from myst.client import Client
from myst.openapi.models.model_fit_policy_list import ModelFitPolicyList


def request_sync(client: Client, project_uuid: str, model_uuid: str) -> ModelFitPolicyList:
    """Lists fit policies for a model."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/models/{model_uuid}/fit_policies/",
        response_class=ModelFitPolicyList,
    )
