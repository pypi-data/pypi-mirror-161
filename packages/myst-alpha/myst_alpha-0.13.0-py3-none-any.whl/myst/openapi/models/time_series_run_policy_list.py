from typing import List

from myst.models import base_model
from myst.openapi.models.time_series_run_policy_get import TimeSeriesRunPolicyGet


class TimeSeriesRunPolicyList(base_model.BaseModel):
    """Schema for time series run policy list responses."""

    data: List[TimeSeriesRunPolicyGet]
    has_more: bool
