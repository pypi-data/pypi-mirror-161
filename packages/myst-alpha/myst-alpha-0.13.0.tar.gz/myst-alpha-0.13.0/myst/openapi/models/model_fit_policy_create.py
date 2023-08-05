from typing import Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.cron_timing_create import CronTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


class ModelFitPolicyCreate(base_model.BaseModel):
    """Schema for model fit policy create requests."""

    object_: Literal["Policy"] = Field(..., alias="object")
    schedule_timing: Union[AbsoluteTimingCreate, RelativeTimingCreate, CronTimingCreate]
    start_timing: Union[AbsoluteTimingCreate, RelativeTimingCreate]
    end_timing: Union[AbsoluteTimingCreate, RelativeTimingCreate]
    type: Optional[Literal["ModelFitPolicy"]] = "ModelFitPolicy"
    active: Optional[bool] = True
