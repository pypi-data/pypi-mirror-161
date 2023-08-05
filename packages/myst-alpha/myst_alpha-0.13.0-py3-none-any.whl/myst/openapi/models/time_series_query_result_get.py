from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.models.time_dataset import TimeDataset


class TimeSeriesQueryResultGet(base_model.BaseModel):
    """Time series query result schema for get responses."""

    object_: Literal["NodeResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["TimeSeriesQueryResult"]
    node: str
    time_dataset: TimeDataset
    update_time: Optional[str] = None
