from myst.client import Client
from myst.openapi.models.layer_create import LayerCreate
from myst.openapi.models.layer_get import LayerGet


def request_sync(client: Client, project_uuid: str, time_series_uuid: str, json_body: LayerCreate) -> LayerGet:
    """Creates a layer for a time series."""

    return client.request(
        method="post",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/layers/",
        response_class=LayerGet,
        request_model=json_body,
    )
