from myst.client import Client
from myst.openapi.models.model_fit_policy_create import ModelFitPolicyCreate
from myst.openapi.models.model_fit_policy_get import ModelFitPolicyGet


def request_sync(
    client: Client, project_uuid: str, model_uuid: str, json_body: ModelFitPolicyCreate
) -> ModelFitPolicyGet:
    """Creates a model fit policy."""

    return client.request(
        method="post",
        path=f"/projects/{project_uuid}/models/{model_uuid}/fit_policies/",
        response_class=ModelFitPolicyGet,
        request_model=json_body,
    )
