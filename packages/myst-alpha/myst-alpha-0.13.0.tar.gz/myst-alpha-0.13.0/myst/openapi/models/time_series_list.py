from typing import List

from myst.models import base_model
from myst.openapi.models.time_series_get import TimeSeriesGet


class TimeSeriesList(base_model.BaseModel):
    """Schema for time series list responses."""

    data: List[TimeSeriesGet]
    has_more: bool
