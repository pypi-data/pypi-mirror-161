from myst.client import Client
from myst.openapi.models.project_get import ProjectGet


def request_sync(client: Client, uuid: str) -> ProjectGet:
    """Deletes a project."""

    return client.request(method="delete", path=f"/projects/{uuid}", response_class=ProjectGet)
