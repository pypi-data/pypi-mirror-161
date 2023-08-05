from myst.client import Client
from myst.openapi.models.layer_get import LayerGet
from myst.openapi.models.layer_update import LayerUpdate


def request_sync(
    client: Client, project_uuid: str, time_series_uuid: str, uuid: str, json_body: LayerUpdate
) -> LayerGet:
    """Updates an existing layer for a time series."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/layers/{uuid}",
        response_class=LayerGet,
        request_model=json_body,
    )
