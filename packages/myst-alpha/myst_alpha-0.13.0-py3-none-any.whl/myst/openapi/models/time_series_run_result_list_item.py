from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class TimeSeriesRunResultListItem(base_model.BaseModel):
    """Schema for time series run result get responses."""

    object_: Literal["NodeResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["TimeSeriesRunResult"]
    node: str
    start_time: str
    end_time: str
    as_of_time: str
    update_time: Optional[str] = None
