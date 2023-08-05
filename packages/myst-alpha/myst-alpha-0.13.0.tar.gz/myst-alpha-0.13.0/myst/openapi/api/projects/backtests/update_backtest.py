from myst.client import Client
from myst.openapi.models.backtest_get import BacktestGet
from myst.openapi.models.backtest_update import BacktestUpdate


def request_sync(client: Client, project_uuid: str, uuid: str, json_body: BacktestUpdate) -> BacktestGet:
    """Updates a backtest."""

    return client.request(
        method="patch",
        path=f"/projects/{project_uuid}/backtests/{uuid}",
        response_class=BacktestGet,
        request_model=json_body,
    )
