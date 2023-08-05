from typing import List

from myst.models import base_model
from myst.openapi.models.backtest_job_get import BacktestJobGet


class ProjectBacktestJobList(base_model.BaseModel):
    """Backtest job list schema."""

    data: List[BacktestJobGet]
    has_more: bool
