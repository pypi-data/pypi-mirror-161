from myst.client import Client
from myst.openapi.models.model_fit_policy_get import ModelFitPolicyGet
from myst.openapi.models.model_fit_policy_update import ModelFitPolicyUpdate


def request_sync(
    client: Client, project_uuid: str, model_uuid: str, uuid: str, json_body: ModelFitPolicyUpdate
) -> ModelFitPolicyGet:
    """Updates a model fit policy."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/models/{model_uuid}/fit_policies/{uuid}",
        response_class=ModelFitPolicyGet,
        request_model=json_body,
    )
