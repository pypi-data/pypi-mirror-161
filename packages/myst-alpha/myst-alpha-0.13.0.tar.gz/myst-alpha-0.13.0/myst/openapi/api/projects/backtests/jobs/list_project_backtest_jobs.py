from myst.client import Client
from myst.openapi.models.project_backtest_job_list import ProjectBacktestJobList


def request_sync(client: Client, project_uuid: str) -> ProjectBacktestJobList:
    """List all backtest jobs for the project."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/backtests/-/jobs/", response_class=ProjectBacktestJobList
    )
