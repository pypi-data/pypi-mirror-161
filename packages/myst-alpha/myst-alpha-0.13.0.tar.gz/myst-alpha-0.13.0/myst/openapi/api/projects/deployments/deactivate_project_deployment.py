from myst.client import Client
from myst.openapi.models.deployment_get import DeploymentGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> DeploymentGet:
    """Deactivates a deployment for a given project."""

    return client.request(
        method="post", path=f"/projects/{project_uuid}/deployments/{uuid}:deactivate", response_class=DeploymentGet
    )
