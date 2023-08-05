from typing import Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.cron_timing_create import CronTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


class BacktestUpdate(base_model.BaseModel):
    """Schema for backtest update requests."""

    object_: Optional[Literal["Backtest"]] = Field("Backtest", alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    test_start_time: Optional[str] = None
    test_end_time: Optional[str] = None
    fit_start_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
    fit_end_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
    fit_reference_timing: Optional[Union[AbsoluteTimingCreate, CronTimingCreate]] = None
    predict_start_timing: Optional[RelativeTimingCreate] = None
    predict_end_timing: Optional[RelativeTimingCreate] = None
    predict_reference_timing: Optional[CronTimingCreate] = None
    model: Optional[str] = None
    creator: Optional[str] = None
