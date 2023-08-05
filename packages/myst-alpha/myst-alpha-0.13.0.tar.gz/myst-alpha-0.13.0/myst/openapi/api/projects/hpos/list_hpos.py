from myst.client import Client
from myst.openapi.models.hpo_get_list import HPOGetList


def request_sync(client: Client, project_uuid: str) -> HPOGetList:
    """Lists all HPOs in the project."""

    return client.request(method="get", path=f"/projects/{project_uuid}/hpos/-/", response_class=HPOGetList)
