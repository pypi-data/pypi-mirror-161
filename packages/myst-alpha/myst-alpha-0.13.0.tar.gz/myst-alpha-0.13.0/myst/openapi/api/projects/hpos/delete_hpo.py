from myst.client import Client
from myst.openapi.models.hpo_get import HPOGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> HPOGet:
    """Deletes an HPO in the project."""

    return client.request(method="delete", path=f"/projects/{project_uuid}/hpos/{uuid}", response_class=HPOGet)
