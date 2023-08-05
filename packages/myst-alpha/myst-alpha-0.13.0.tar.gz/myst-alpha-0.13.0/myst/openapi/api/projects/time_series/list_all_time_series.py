from myst.client import Client
from myst.openapi.models.time_series_list import TimeSeriesList


def request_sync(client: Client) -> TimeSeriesList:
    """Lists time series across all projects."""

    return client.request(method="get", path=f"/projects/-/time_series/", response_class=TimeSeriesList)
