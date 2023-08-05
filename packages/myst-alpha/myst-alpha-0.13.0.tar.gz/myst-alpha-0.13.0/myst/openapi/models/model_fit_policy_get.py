from typing import Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_get import AbsoluteTimingGet
from myst.openapi.models.cron_timing_get import CronTimingGet
from myst.openapi.models.relative_timing_get import RelativeTimingGet


class ModelFitPolicyGet(base_model.BaseModel):
    """Schema for model fit policy get responses."""

    object_: Literal["Policy"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["ModelFitPolicy"]
    creator: str
    schedule_timing: Union[AbsoluteTimingGet, RelativeTimingGet, CronTimingGet]
    active: bool
    node: str
    start_timing: Union[AbsoluteTimingGet, RelativeTimingGet]
    end_timing: Union[AbsoluteTimingGet, RelativeTimingGet]
    update_time: Optional[str] = None
