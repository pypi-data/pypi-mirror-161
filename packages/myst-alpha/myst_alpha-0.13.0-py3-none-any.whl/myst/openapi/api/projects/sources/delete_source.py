from myst.client import Client
from myst.openapi.models.source_get import SourceGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> SourceGet:
    """Deletes a source."""

    return client.request(method="delete", path=f"/projects/{project_uuid}/sources/{uuid}", response_class=SourceGet)
