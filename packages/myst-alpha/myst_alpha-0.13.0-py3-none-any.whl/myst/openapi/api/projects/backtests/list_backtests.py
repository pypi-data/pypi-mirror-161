from myst.client import Client
from myst.openapi.models.backtest_list import BacktestList


def request_sync(client: Client, project_uuid: str) -> BacktestList:
    """Lists backtests."""

    return client.request(method="get", path=f"/projects/{project_uuid}/backtests/", response_class=BacktestList)
