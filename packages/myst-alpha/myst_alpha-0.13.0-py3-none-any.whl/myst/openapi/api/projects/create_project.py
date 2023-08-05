from myst.client import Client
from myst.openapi.models.project_create import ProjectCreate
from myst.openapi.models.project_get import ProjectGet


def request_sync(client: Client, json_body: ProjectCreate) -> ProjectGet:
    """Creates a project."""

    return client.request(method="post", path=f"/projects/", response_class=ProjectGet, request_model=json_body)
