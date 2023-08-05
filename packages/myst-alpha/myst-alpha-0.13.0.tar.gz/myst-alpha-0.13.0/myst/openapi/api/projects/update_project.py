from myst.client import Client
from myst.openapi.models.project_get import ProjectGet
from myst.openapi.models.project_update import ProjectUpdate


def request_sync(client: Client, uuid: str, json_body: ProjectUpdate) -> ProjectGet:
    """Updates a project."""

    return client.request(method="patch", path=f"/projects/{uuid}", response_class=ProjectGet, request_model=json_body)
