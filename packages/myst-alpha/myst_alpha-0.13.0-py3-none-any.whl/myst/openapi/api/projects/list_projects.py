from myst.client import Client
from myst.openapi.models.project_list import ProjectList


def request_sync(client: Client) -> ProjectList:
    """Lists projects."""

    return client.request(method="get", path=f"/projects/", response_class=ProjectList)
