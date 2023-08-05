from myst.client import Client
from myst.openapi.models.source_get import SourceGet
from myst.openapi.models.source_update import SourceUpdate


def request_sync(client: Client, project_uuid: str, uuid: str, json_body: SourceUpdate) -> SourceGet:
    """Updates a source."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/sources/{uuid}",
        response_class=SourceGet,
        request_model=json_body,
    )
