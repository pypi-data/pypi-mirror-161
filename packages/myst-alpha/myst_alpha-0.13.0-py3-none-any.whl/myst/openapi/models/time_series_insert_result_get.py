from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class TimeSeriesInsertResultGet(base_model.BaseModel):
    """Time series insert result schema for get responses."""

    object_: Literal["NodeResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["TimeSeriesInsertResult"]
    node: str
    update_time: Optional[str] = None
