from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class RelativeTimingGet(base_model.BaseModel):
    """Relative timing schema for get responses."""

    object_: Literal["Timing"] = Field(..., alias="object")
    type: Literal["RelativeTiming"]
    frequency: Optional[str] = None
    offset: Optional[str] = None
    time_zone: Optional[str] = None
