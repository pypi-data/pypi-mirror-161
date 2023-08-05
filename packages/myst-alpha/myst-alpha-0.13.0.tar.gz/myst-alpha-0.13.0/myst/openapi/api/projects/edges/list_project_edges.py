from myst.client import Client
from myst.openapi.models.project_edges_list import ProjectEdgesList


def request_sync(client: Client, project_uuid: str) -> ProjectEdgesList:
    """List edges for a given project."""

    return client.request(method="get", path=f"/projects/{project_uuid}/edges/", response_class=ProjectEdgesList)
