from myst.client import Client
from myst.openapi.models.time_series_run_result_get import TimeSeriesRunResultGet


def request_sync(client: Client, project_uuid: str, time_series_uuid: str, uuid: str) -> TimeSeriesRunResultGet:
    """Gets a time series run result by its unique identifier."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/run_results/{uuid}",
        response_class=TimeSeriesRunResultGet,
    )
