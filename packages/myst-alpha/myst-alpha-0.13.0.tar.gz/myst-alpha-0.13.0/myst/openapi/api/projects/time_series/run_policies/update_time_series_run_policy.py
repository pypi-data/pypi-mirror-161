from myst.client import Client
from myst.openapi.models.time_series_run_policy_get import TimeSeriesRunPolicyGet
from myst.openapi.models.time_series_run_policy_update import TimeSeriesRunPolicyUpdate


def request_sync(
    client: Client, project_uuid: str, time_series_uuid: str, uuid: str, json_body: TimeSeriesRunPolicyUpdate
) -> TimeSeriesRunPolicyGet:
    """Updates a time series run policy."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/run_policies/{uuid}",
        response_class=TimeSeriesRunPolicyGet,
        request_model=json_body,
    )
