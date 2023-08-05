from myst.client import Client
from myst.openapi.models.deployment_create import DeploymentCreate
from myst.openapi.models.deployment_get import DeploymentGet


def request_sync(client: Client, project_uuid: str, json_body: DeploymentCreate) -> DeploymentGet:
    """Creates a deployment for a given project, deactivating any currently active deployment."""

    return client.request(
        method="post",
        path=f"/projects/{project_uuid}/deployments/",
        response_class=DeploymentGet,
        request_model=json_body,
    )
