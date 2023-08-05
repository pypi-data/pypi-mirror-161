from myst.client import Client
from myst.openapi.models.project_create import ProjectCreate
from myst.openapi.models.project_get import ProjectGet


def request_sync(client: Client, uuid: str, json_body: ProjectCreate) -> ProjectGet:
    """Creates a copy of an existing project."""

    return client.request(
        method="post", path=f"/projects/{uuid}:copy", response_class=ProjectGet, request_model=json_body
    )
