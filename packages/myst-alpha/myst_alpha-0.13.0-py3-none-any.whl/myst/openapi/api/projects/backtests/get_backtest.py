from myst.client import Client
from myst.openapi.models.backtest_get import BacktestGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> BacktestGet:
    """Gets a backtest by its unique identifier."""

    return client.request(method="get", path=f"/projects/{project_uuid}/backtests/{uuid}", response_class=BacktestGet)
