from myst.client import Client
from myst.openapi.models.layer_list import LayerList


def request_sync(client: Client, project_uuid: str, time_series_uuid: str) -> LayerList:
    """Lists layers for a time series."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/layers/", response_class=LayerList
    )
