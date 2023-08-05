from myst.client import Client
from myst.openapi.models.backtest_get import BacktestGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> BacktestGet:
    """Deletes a backtest."""

    return client.request(
        method="delete", path=f"/projects/{project_uuid}/backtests/{uuid}", response_class=BacktestGet
    )
