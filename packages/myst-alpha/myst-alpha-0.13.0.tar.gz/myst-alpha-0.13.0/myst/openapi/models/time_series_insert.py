from myst.models import base_model
from myst.models.time_dataset import TimeDataset


class TimeSeriesInsert(base_model.BaseModel):
    """Schema for time series insert requests."""

    time_dataset: TimeDataset
