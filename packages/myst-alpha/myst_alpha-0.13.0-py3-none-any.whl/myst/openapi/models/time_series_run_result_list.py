from typing import List

from myst.models import base_model
from myst.openapi.models.time_series_run_result_list_item import TimeSeriesRunResultListItem


class TimeSeriesRunResultList(base_model.BaseModel):
    """Schema for time series run result list responses."""

    data: List[TimeSeriesRunResultListItem]
    has_more: bool
