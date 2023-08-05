from myst.client import Client
from myst.openapi.models.backtest_create import BacktestCreate
from myst.openapi.models.backtest_get import BacktestGet


def request_sync(client: Client, project_uuid: str, json_body: BacktestCreate) -> BacktestGet:
    """Creates a backtest."""

    return client.request(
        method="post", path=f"/projects/{project_uuid}/backtests/", response_class=BacktestGet, request_model=json_body
    )
