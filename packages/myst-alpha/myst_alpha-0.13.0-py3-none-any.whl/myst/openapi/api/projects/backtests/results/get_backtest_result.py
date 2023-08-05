from typing import Any, Dict

from myst.client import Client
from myst.openapi.models.backtest_result_get import BacktestResultGet


def request_sync(client: Client, project_uuid: str, backtest_uuid: str, job_uuid: str) -> BacktestResultGet:
    """Gets a backtest result by its unique identifier."""

    params: Dict[str, Any] = {"job_uuid": job_uuid}
    params = {k: v for k, v in params.items() if v is not None}

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/backtests/{backtest_uuid}/results/",
        response_class=BacktestResultGet,
        params=params,
    )
