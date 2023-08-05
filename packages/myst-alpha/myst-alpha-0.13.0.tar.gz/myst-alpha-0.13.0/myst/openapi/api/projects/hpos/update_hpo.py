from myst.client import Client
from myst.openapi.models.hpo_get import HPOGet
from myst.openapi.models.hpo_update import HPOUpdate


def request_sync(client: Client, project_uuid: str, uuid: str, json_body: HPOUpdate) -> HPOGet:
    """Updates an HPO in the project."""

    return client.request(
        method="patch", path=f"/projects/{project_uuid}/hpos/{uuid}", response_class=HPOGet, request_model=json_body
    )
