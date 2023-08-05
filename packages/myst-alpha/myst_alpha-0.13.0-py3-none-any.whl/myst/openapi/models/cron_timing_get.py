from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class CronTimingGet(base_model.BaseModel):
    """Cron timing schema for get responses."""

    object_: Literal["Timing"] = Field(..., alias="object")
    type: Literal["CronTiming"]
    cron_expression: str
    time_zone: str
