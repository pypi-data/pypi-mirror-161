from myst.client import Client
from myst.openapi.models.hpo_create import HPOCreate
from myst.openapi.models.hpo_get import HPOGet


def request_sync(client: Client, project_uuid: str, json_body: HPOCreate) -> HPOGet:
    """Creates an HPO in the project."""

    return client.request(
        method="post", path=f"/projects/{project_uuid}/hpos/", response_class=HPOGet, request_model=json_body
    )
