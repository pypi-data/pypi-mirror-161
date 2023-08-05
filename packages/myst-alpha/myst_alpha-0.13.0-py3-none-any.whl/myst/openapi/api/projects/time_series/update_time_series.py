from myst.client import Client
from myst.openapi.models.time_series_get import TimeSeriesGet
from myst.openapi.models.time_series_update import TimeSeriesUpdate


def request_sync(client: Client, project_uuid: str, uuid: str, json_body: TimeSeriesUpdate) -> TimeSeriesGet:
    """Updates a time series."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/time_series/{uuid}",
        response_class=TimeSeriesGet,
        request_model=json_body,
    )
