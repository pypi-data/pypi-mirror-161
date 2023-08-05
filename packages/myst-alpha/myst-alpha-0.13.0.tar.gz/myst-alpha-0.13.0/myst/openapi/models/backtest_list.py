from typing import List

from myst.models import base_model
from myst.openapi.models.backtest_get import BacktestGet


class BacktestList(base_model.BaseModel):
    """Schema for backtest list responses."""

    data: List[BacktestGet]
    has_more: bool
