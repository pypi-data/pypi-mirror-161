from myst.client import Client
from myst.openapi.models.source_create import SourceCreate
from myst.openapi.models.source_get import SourceGet


def request_sync(client: Client, project_uuid: str, json_body: SourceCreate) -> SourceGet:
    """Creates a source."""

    return client.request(
        method="post", path=f"/projects/{project_uuid}/sources/", response_class=SourceGet, request_model=json_body
    )
