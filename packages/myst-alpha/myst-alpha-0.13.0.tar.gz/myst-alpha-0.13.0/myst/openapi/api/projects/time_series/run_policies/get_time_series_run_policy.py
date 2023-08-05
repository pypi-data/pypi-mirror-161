from myst.client import Client
from myst.openapi.models.time_series_run_policy_get import TimeSeriesRunPolicyGet


def request_sync(client: Client, project_uuid: str, time_series_uuid: str, uuid: str) -> TimeSeriesRunPolicyGet:
    """Gets a time series run policy by its unique identifier."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/run_policies/{uuid}",
        response_class=TimeSeriesRunPolicyGet,
    )
