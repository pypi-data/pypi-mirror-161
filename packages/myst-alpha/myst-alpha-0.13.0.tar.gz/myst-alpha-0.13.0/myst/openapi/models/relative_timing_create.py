from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class RelativeTimingCreate(base_model.BaseModel):
    """Relative timing schema for create requests."""

    type: Literal["RelativeTiming"]
    object_: Optional[Literal["Timing"]] = Field("Timing", alias="object")
    frequency: Optional[str] = None
    offset: Optional[str] = None
    time_zone: Optional[str] = None
