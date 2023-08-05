from myst.client import Client
from myst.openapi.models.backtest_job_get import BacktestJobGet


def request_sync(client: Client, project_uuid: str, backtest_uuid: str, uuid: str) -> BacktestJobGet:
    """List all backtest jobs for the project."""

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/backtests/{backtest_uuid}/jobs/{uuid}",
        response_class=BacktestJobGet,
    )
