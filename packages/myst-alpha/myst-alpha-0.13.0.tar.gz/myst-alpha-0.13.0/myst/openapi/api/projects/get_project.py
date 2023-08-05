from myst.client import Client
from myst.openapi.models.project_get import ProjectGet


def request_sync(client: Client, uuid: str) -> ProjectGet:
    """Gets a project by its unique identifier."""

    return client.request(method="get", path=f"/projects/{uuid}", response_class=ProjectGet)
