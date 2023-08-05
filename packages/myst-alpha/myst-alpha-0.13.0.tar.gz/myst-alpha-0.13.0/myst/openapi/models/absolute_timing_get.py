from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class AbsoluteTimingGet(base_model.BaseModel):
    """Absolute timing schema for get responses."""

    object_: Literal["Timing"] = Field(..., alias="object")
    type: Literal["AbsoluteTiming"]
    time: str
