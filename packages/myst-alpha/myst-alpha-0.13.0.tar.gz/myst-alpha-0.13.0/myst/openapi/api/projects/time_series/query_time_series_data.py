from typing import Any, Dict, Optional

from myst.client import Client
from myst.openapi.models.time_series_query_result_get import TimeSeriesQueryResultGet


def request_sync(
    client: Client,
    project_uuid: str,
    uuid: str,
    start_time: str,
    end_time: str,
    as_of_time: Optional[str] = None,
    as_of_offset: Optional[str] = None,
) -> TimeSeriesQueryResultGet:
    """Queries time series data."""

    params: Dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "as_of_time": as_of_time,
        "as_of_offset": as_of_offset,
    }
    params = {k: v for k, v in params.items() if v is not None}

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/time_series/{uuid}:query",
        response_class=TimeSeriesQueryResultGet,
        params=params,
    )
