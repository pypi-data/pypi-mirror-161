from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class CronTimingCreate(base_model.BaseModel):
    """Cron timing schema for create requests."""

    type: Literal["CronTiming"]
    cron_expression: str
    object_: Optional[Literal["Timing"]] = Field("Timing", alias="object")
    time_zone: Optional[str] = "UTC"
