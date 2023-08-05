from typing import Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.cron_timing_create import CronTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


class ModelFitPolicyUpdate(base_model.BaseModel):
    """Schema for model fit policy update requests."""

    object_: Optional[Literal["Policy"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    type: Optional[Literal["ModelFitPolicy"]] = None
    creator: Optional[str] = None
    schedule_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate, CronTimingCreate]] = None
    active: Optional[bool] = None
    node: Optional[str] = None
    start_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
    end_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
