from myst.client import Client
from myst.openapi.models.time_series_run_result_list import TimeSeriesRunResultList


def request_sync(client: Client, project_uuid: str, time_series_uuid: str) -> TimeSeriesRunResultList:
    """Lists time series run results for the given time series."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/run_results/",
        response_class=TimeSeriesRunResultList,
    )
