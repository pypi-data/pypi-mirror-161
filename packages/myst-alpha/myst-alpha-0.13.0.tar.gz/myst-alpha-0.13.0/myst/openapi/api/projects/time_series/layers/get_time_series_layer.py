from myst.client import Client
from myst.openapi.models.layer_get import LayerGet


def request_sync(client: Client, project_uuid: str, time_series_uuid: str, uuid: str) -> LayerGet:
    """Gets a specific layer for a time series."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/layers/{uuid}",
        response_class=LayerGet,
    )
