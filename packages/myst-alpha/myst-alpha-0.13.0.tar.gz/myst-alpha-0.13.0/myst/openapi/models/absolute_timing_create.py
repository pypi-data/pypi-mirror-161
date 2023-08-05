from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class AbsoluteTimingCreate(base_model.BaseModel):
    """Absolute timing schema for create requests."""

    type: Literal["AbsoluteTiming"]
    time: str
    object_: Optional[Literal["Timing"]] = Field("Timing", alias="object")
