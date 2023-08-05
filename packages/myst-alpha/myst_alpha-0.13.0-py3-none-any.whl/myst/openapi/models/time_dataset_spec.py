from typing import List, Union

from myst.models import base_model


class TimeDatasetSpec(base_model.BaseModel):
    """A custom schema that represents the `spec` of a `TimeDataset`."""

    sample_period: str
    cell_shape: List[int]
    coordinate_labels: List[List[Union[int, str]]]
    axis_labels: List[Union[int, str]]
