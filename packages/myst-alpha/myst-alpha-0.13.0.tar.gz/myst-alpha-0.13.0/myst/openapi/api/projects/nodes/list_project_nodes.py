from myst.client import Client
from myst.openapi.models.project_nodes_list import ProjectNodesList


def request_sync(client: Client, project_uuid: str) -> ProjectNodesList:
    """Lists nodes for a given project."""

    return client.request(method="get", path=f"/projects/{project_uuid}/nodes/", response_class=ProjectNodesList)
