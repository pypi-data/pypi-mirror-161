from myst.client import Client
from myst.openapi.models.deployment_list import DeploymentList


def request_sync(client: Client, project_uuid: str) -> DeploymentList:
    """Lists deployments for a given project."""

    return client.request(method="get", path=f"/projects/{project_uuid}/deployments/", response_class=DeploymentList)
