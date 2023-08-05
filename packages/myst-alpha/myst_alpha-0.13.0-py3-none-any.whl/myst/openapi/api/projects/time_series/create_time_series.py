from myst.client import Client
from myst.openapi.models.time_series_create import TimeSeriesCreate
from myst.openapi.models.time_series_get import TimeSeriesGet


def request_sync(client: Client, project_uuid: str, json_body: TimeSeriesCreate) -> TimeSeriesGet:
    """Creates a time series."""

    return client.request(
        method="post",
        path=f"/projects/{project_uuid}/time_series/",
        response_class=TimeSeriesGet,
        request_model=json_body,
    )
