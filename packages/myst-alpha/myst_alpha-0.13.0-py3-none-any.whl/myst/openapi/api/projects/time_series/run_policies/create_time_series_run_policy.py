from myst.client import Client
from myst.openapi.models.time_series_run_policy_create import TimeSeriesRunPolicyCreate
from myst.openapi.models.time_series_run_policy_get import TimeSeriesRunPolicyGet


def request_sync(
    client: Client, project_uuid: str, time_series_uuid: str, json_body: TimeSeriesRunPolicyCreate
) -> TimeSeriesRunPolicyGet:
    """Creates a time series run policy."""

    return client.request(
        method="post",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/run_policies/",
        response_class=TimeSeriesRunPolicyGet,
        request_model=json_body,
    )
