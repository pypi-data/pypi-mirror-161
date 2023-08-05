from myst.client import Client
from myst.openapi.models.project_node_result_list import ProjectNodeResultList


def request_sync(client: Client, project_uuid: str) -> ProjectNodeResultList:
    """Lists results."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/nodes/-/results/", response_class=ProjectNodeResultList
    )
