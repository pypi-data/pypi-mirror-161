from myst.client import Client
from myst.openapi.models.time_series_run_policy_list import TimeSeriesRunPolicyList


def request_sync(client: Client, project_uuid: str, time_series_uuid: str) -> TimeSeriesRunPolicyList:
    """Lists run policies for a time_series."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/time_series/{time_series_uuid}/run_policies/",
        response_class=TimeSeriesRunPolicyList,
    )
