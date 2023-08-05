from myst.client import Client
from myst.openapi.models.time_series_get import TimeSeriesGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> TimeSeriesGet:
    """Deletes a time series."""

    return client.request(
        method="delete", path=f"/projects/{project_uuid}/time_series/{uuid}", response_class=TimeSeriesGet
    )
